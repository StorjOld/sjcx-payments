#!/usr/local/bin/python3
import time
import csv
import xlrd
from math import exp
import exchange_rates
import requests
import re
import datetime as dt
from pymongo import MongoClient
import sqlite3


SJCX_TOTAL_REWARDS = 100000
PAST_REWARDS_CSV = "Storj Test Group B Rewards Compliance.xlsx"
SECONDS_IN_TWO_WEEKS = 1209600
SECONDS_IN_MONTH = 2678400
INDIVIDUAL_MAX_HEIGHT = 199999
SJCX_BALANCE_API = "http://xcp.blockscan.com/api2?module=asset&action=holders&name=sjcx"
WHITELIST = 'https://raw.githubusercontent.com/Storj/whitelist/master/storj_crowdfunding_by_amount.txt'


def gb_from_height(height):
    """Returns the size in gigabytes of the height.

    Args:
        height: farmer's capacity (number of 128MB shards it can store)

    Returns:
        gb: gigabytes
    """
    gb = float(height*128*1048576/1000000000)
    return gb


def distinct_farmers(collection, first_date, last_date):
    """Returns list of distinct authentication addresses seen between
    first_date and last_date.

    Args:
        collection: MongoDB collection of data on farmers
        first_date: first datetime in date range
        last_date: last datetime in date range

    Returns:
        farmers: list of distinct btc_addr (authentication addresses)
                 recorded in the collection between first_date and last_date
    """
    farmers = collection.find({'time': {'$gte': first_date, '$lte': last_date}}
                              ).distinct('btc_addr')
    return farmers


def average_height(btc_address, first_date, last_date, collection):
    """Returns the average height of the specified btc address
    between the first_date and last_date.

    Args:
        btc_address: btc_address (authentication address) for farmer
        first_date: first datetime in date range
        last_date: last datetime in date range
        collection: MongoDB collection of data on farmers

    Returns:
        avg_height: average height of the build with btc_address between
                    first_date and last_date
    """
    pipeline = [
        {'$match': {'farmers.btc_addr': btc_address,
                    'time': {'$gte': first_date, '$lt': last_date}}},
        {'$project': {'_id': 0, 'farmers.btc_addr': 1, 'farmers.height': 1}},
        {'$unwind': '$farmers'},
        {'$match': {'farmers.btc_addr': btc_address}}
    ]
    height_array = []
    for doc in collection.aggregate(pipeline):
        height_array.append(doc['farmers']['height'])
    return sum(height_array)/len(height_array)


def create_table(conn, cursor):
    """Creates the rewards table.

    Args:
        conn: sqlite connection
        cursor: conn's cursor
    """
    cursor.execute('''CREATE TABLE rewards
        (auth_address      CHAR(34)               NOT NULL,
         payment_date      TEXT                   NOT NULL,
         duration          REAL,
         uptime            REAL,
         height            REAL,
         payout_address    CHAR(34),
         balance           REAL    default 0,
         points            REAL    default 0,
         sjcx_reward       REAL    default 0,
         usd_reward        REAL    default 0,
         total_usd_reward REAL    default 0,
         PRIMARY KEY (auth_address, payment_date));''')
    conn.commit()


def add_reward_stats(conn, cursor, collection, first_date, last_date):
    """Add the duration, uptime, and height statistics for the farmers
    who were online between first_date and last_date.

    Args:
        conn: sqlite connection
        cursor: conn's cursor
        collection: MongoDB collection of data on farmers
        first_date: first datetime in date range
        last_date: last datetime in date range
    """
    first_dates = {}
    last_dates = {}
    uptimes = {}
    previous_time = 0
    for doc in collection.find({'time': {'$gte': first_date,
                                         '$lt': last_date}}).sort('time', 1):
        doc_time = time.mktime(doc['time'].timetuple())
        for farmer in doc['farmers']:
            auth_address = farmer['btc_addr']
            if auth_address in first_dates:
                if last_dates[auth_address] == previous_time:
                    uptimes[auth_address] += doc_time - previous_time
                last_dates[auth_address] = doc_time
            else:
                first_dates[auth_address] = doc_time
                last_dates[auth_address] = doc_time
                uptimes[auth_address] = 0
        previous_time = doc_time
    for key, value in first_dates.items():
        address = key
        duration = last_dates[key] - value
        uptime = uptimes[key]
        avg_height = average_height(key, first_date, last_date, collection)
        cursor.execute('''INSERT INTO rewards (auth_address, payment_date, duration,
                          uptime, height) VALUES(?, ?, ?, ?, ?)''',
                       (str(address), last_date, duration, uptime, avg_height))
        conn.commit()


def add_payout_address(conn, cursor, collection):
    """Add payout address info for all the authentication addresses in the
    sqlite db.

    Args:
        conn: sqlite3 connection
        cursor: conn's cursor
        collection: MongoDB collection of data on farmers
    """
    cursor.execute('''SELECT auth_address FROM rewards''')
    auth_addresses = cursor.fetchall()
    for auth_address in auth_addresses:
        auth_address = ''.join(auth_address)
        pipeline = [
            {'$match': {'farmers.btc_addr': auth_address}},
            {'$project': {'_id': 0, 'farmers.btc_addr': 1, 'farmers.payout_addr': 1}},
            {'$unwind': '$farmers'},
            {'$match': {'farmers.btc_addr': auth_address}}
        ]
        for doc in collection.aggregate(pipeline):
            payout_address = doc['farmers']['payout_addr']
            break
        cursor.execute('UPDATE rewards SET payout_address = ? WHERE auth_address = ?',
                       (str(payout_address), str(auth_address),))
    conn.commit()


def create_whitelist():
    """Returns an array of addresses on the whitelist."""
    whitelist = []
    response = requests.get('https://raw.githubusercontent.com/Storj/whitelist/'
                            'master/storj_crowdfunding_by_amount.txt')
    strings = re.findall('"([^"]*)"', response.text)
    for string in strings:
        if len(string) > 30:
            whitelist.append(string)
    return whitelist


def add_balances(conn, cursor, payment_date):
    """Adds balances for payout addresses.

    Args:
        conn: sqlite3 connection
        cursor: conn's cursor
        payment_date: datetime when farmer's rewards are calculated
    """
    response = requests.get(SJCX_BALANCE_API)
    data = response.json()['data']
    for item in data:
        address = item['address']
        balance = float(item['balance'])
        cursor.execute('''UPDATE rewards SET balance=? WHERE payout_address=?
                          AND payment_date=?''',
                       (balance, address, str(payment_date),))
    conn.commit()


def assign_points(conn, cursor, date):
    """Assigns points for each farmer given their uptime, duration, and size.

    Args:
        conn: sqlite3 connection
        cursor: conn's cursor
        date: datetime when farmer's rewards are calculated
    """
    cursor.execute('''SELECT auth_address, payout_address, balance, uptime,
                      duration, height FROM rewards WHERE payment_date=?''',
                   (str(date),))
    address_list = cursor.fetchall()
    whitelist = create_whitelist()
    for item in address_list:
        auth_addr = item[0]
        payout_addr = item[1]
        balance = item[2]
        uptime = item[3]
        duration = item[4]
        height = item[5]
        if duration == 0:
            continue
        elif (balance >= 10000) or (payout_addr in whitelist):
            payment_ratio = 1
            if balance < 10000:
                payment_ratio = float(balance/10000)
            points = payment_ratio * height_function(height) * \
                     uptime_logistic_function(uptime/duration) * \
                     (duration / SECONDS_IN_MONTH)
            cursor.execute('UPDATE rewards SET points=? WHERE auth_address=? AND '
                           'payment_date=?',
                          (points, str(auth_addr), str(date),))
            conn.commit()


def distribute_sjcx(conn, cursor, payment_date):
    """Distributes the sjcx among the farmers and calculates the value
    of the sjcx rewards in dollars.

    Args:
        conn: sqlite3 connection
        cursor: conn's cursor
        payment_date: date when farmer's rewards are calculated
    """
    cursor.execute('SELECT sum(points) FROM rewards WHERE payment_date = ?', (str(payment_date),))
    data = cursor.fetchone()
    total_points = data[0]

    cursor.execute('UPDATE rewards SET sjcx_reward = ? * points / ?',
                   (SJCX_TOTAL_REWARDS, total_points))
    btc_sjcx_rate = exchange_rates.btc_sjcx_rate(payment_date)
    btc_usd_rate = exchange_rates.btc_usd_rate(payment_date)
    cursor.execute('UPDATE rewards SET usd_reward = sjcx_reward * ? * ?',
                   (btc_sjcx_rate, btc_usd_rate))
    conn.commit()


def uptime_logistic_function(uptime):
    """Returns a value between 0 and 1.

    Args:
        uptime: uptime percentage (between 0 and 1)

    Returns:
        value: output of a logistic function for given uptime (ranges between
               0 and 1)
    """
    value = 1 / (1 + exp((-uptime + 0.85) * 19)) + 0.0547
    return value


def height_function(height):
    """Returns value between 0 and 1.

    Args:
        height: farmer's capacity (number of 128MB shards it can store)

    Returns:
        value: output of function y = 0.1 + 0.9 * h (if, h > 0)
                                  y = 0 (if, h == 0)
    """
    if height == 0:
        return 0
    height_percentage = height / INDIVIDUAL_MAX_HEIGHT
    value = 0.01 + 0.99 * height_percentage
    return value


def update_total_rewards(conn, cursor, last_date):
    """Updates the total rewards column for all the farmers.

    Args:
        conn: sqlite3 connection
        cursor: conn's cursor
        last_date: payment date for which to update total rewards
    """
    cursor.execute('SELECT address FROM rewards WHERE payment_date = ?', (str(last_date),))
    address_list = cursor.fetchall()
    for address in address_list:
        address = ''.join(address)
        cursor.execute('''SELECT MAX(total_usd_reward) FROM rewards WHERE
                          address = ?''', (str(address),))
        total_past_rewards = cursor.fetchone()[0]
        cursor.execute('''UPDATE rewards SET total_usd_rewards = ? + usd_reward
                          WHERE address = ? and payment_date = ?''',
                       (total_past_rewards, str(address), str(last_date),))
    conn.commit()


def make_points_csv(cursor, date):
    """Create a rewards csv of how much each farmer should get paid.
    csv is titled 'sjcx_auth_rewards.csv'

    Args:
        cursor: cursor of sqlite3 connection
        date: datetime when payments are calculated
    """
    cursor.execute('''SELECT auth_address, payout_address, sjcx_reward,
                      usd_reward, duration / (86400),
                      uptime / duration * 100, height FROM rewards
                      WHERE duration > 0 AND payment_date=?''', (str(date),))
    csv_file = '../sjcx_rewards_{}_{}_{}.csv'.format(date.year, date.month, date.day)
    with open(csv_file, 'w') as fp:
        csv_writer = csv.writer(fp)
        csv_writer.writerow(['auth_address', 'payout_address', 'sjcx_reward',
                             'usd_reward', 'duration (days)',
                             'uptime percentage', 'average height'])
        csv_writer.writerows(cursor)


def init_past_rewards(conn, cursor):
    """Initialize the table with the past rewards (first three payouts).
    This function should be run once.

    Args:
        conn: sqlite3 connection
        cursor: conn's cursor
    """
    xl_workbook = xlrd.open_workbook(PAST_REWARDS_CSV)
    xl_sheet = xl_workbook.sheet_by_name("Totals")
    for row_idx in range(1, xl_sheet.nrows):
        address = str(xl_sheet.cell(row_idx, 0).value)
        reward = format(float(str(xl_sheet.cell(row_idx, 3).value)), '.2f')
        cursor.execute('''UPDATE rewards SET total_usd_reward = ? + usd_reward
                          WHERE payout_address = ?''', (reward, address))
        conn.commit()
    cursor.execute('''UPDATE rewards SET total_usd_reward = usd_reward
                      WHERE total_usd_reward = 0''')
    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect('../data/rewards.db')
    cursor = conn.cursor()
    connection = MongoClient('localhost', 27017)
    collection = connection['GroupB']['farmers']

    first_date = input('Enter the first date for the payment duration period'
                       'in YYYY-MM-DD format.')
    last_date = input('Enter the last date for the payment duration period'
                      'in YYYY-MM-DD format.')
    first_year, first_month, first_day = map(int, first_date.split('-'))
    last_year, last_month, last_day = map(int, last_date.split('-'))
    first_date = dt.datetime(first_year, first_month, first_day, 0, 0, 0)
    last_date = dt.datetime(last_year, last_month, last_day, 0, 0, 0)

    print('Calculating rewards...')
    add_reward_stats(conn, cursor, collection, first_date, last_date)
    assign_points(conn, cursor, last_date)
    distribute_sjcx(conn, cursor, last_date)
    update_total_rewards(conn, cursor)

    make_points_csv(cursor)
    conn.close()
    print('Open sjcx_rewards.csv to see rewards')
