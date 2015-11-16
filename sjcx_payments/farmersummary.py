#!/usr/local/bin/python3

import sqlite3
from pymongo import MongoClient
import datetime as dt
from datetime import timedelta
import time
from math import exp
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import sjcx_payments.payments as payments


SECONDS_IN_DAY = 86400


def create_summary_table(conn, cursor): # pragma: no cover
    """Create the summaries table."""
    cursor.execute('''CREATE TABLE summaries
                      (payout_address CHAR(34)     NOT NULL,
                      date            TEXT         NOT NULL,
                      auth_address    TEXT         NOT NULL,
                      uptime          REAL,
                      duration        REAL,
                      height          INTEGER,
                      points          REAL  default 0,
                      percentage      REAL,
                      PRIMARY KEY (auth_address, date));''')
    conn.commit()


def init_table(conn, cursor, collection):
    """Initializes the summaries table."""
    client = MongoClient('localhost', 27017)
    collection = client['GroupB']['farmers']
    first_date = begin_date(collection)
    last_date = end_date((collection))
    day_count = (last_date - first_date).days
    for single_date in (first_date + timedelta(days=n) for n in range(day_count)):
        create_daily_summary(conn, cursor, collection, single_date)
        assign_points(conn, cursor, single_date)
        assign_percentages(conn, cursor, single_date)


def update_table(conn, cursor, collection): # pragma: no cover
    """Updates the summaries table if there is new data in collection."""
    cursor.execute('SELECT MAX(date) FROM summaries')
    date = cursor.fetchone()[0]
    max_date = dt.strptime(date,  '%Y-%M-%D %H:%M:%S')
    next_date = max_date + timedelta(days = 1)
    last_date = end_date(collection)
    day_count = (last_date - next_date).days
    for single_date in (next_date + timedelta(days=n) for n in range(day_count)):
        create_daily_summary(conn, cursor, collection, single_date)
        assign_points(conn, cursor, single_date)
        assign_percentages(conn, cursor, single_date)


def create_daily_summary(conn, cursor, collection, date):
    """
    Inserts the farmers' summaries for the specified date.

    Args:
        conn: sqlite db connection
        cursor: conn's cursor
        collection: MongoDB farmers collection
        date: generate summary entries for this date
    """
    next_date = date + timedelta(days = 1)
    first_dates = {}
    last_dates = {}
    payout_addresses = {}
    uptimes = {}
    previous_time = 0
    for doc in collection.find({'time': {'$gte': date, '$lt': next_date}}):
        doc_time = time.mktime(doc['time'].timetuple())
        for farmer in doc['farmers']:
            auth_address = farmer['btc_addr']
            if (auth_address in first_dates):
                if last_dates[auth_address] == previous_time:
                    uptimes[auth_address] += doc_time - previous_time
                last_dates[auth_address] = doc_time
            else:
                first_dates[auth_address] = doc_time
                last_dates[auth_address] = doc_time
                payout_addresses[auth_address] = farmer['payout_addr']
                uptimes[auth_address] = 0
        previous_time = doc_time
    for key in first_dates:
        auth_address = key
        summary_date = date
        payout_address = payout_addresses[key]
        uptime = uptimes[key]
        duration = last_dates[key] - first_dates[key]
        height = payments.average_height(auth_address, date, next_date, collection)
        cursor.execute('''INSERT INTO summaries (auth_address, date,
                          payout_address, uptime, duration, height)
                          VALUES (?, ?, ?, ?, ? ,?)''',
                       (str(auth_address), str(summary_date), payout_address, uptime,
                       duration, height))
        conn.commit()


def assign_points(conn, cursor, date):
    """Returns the number of points awarded for the given size,
    uptime, and duration."""
    cursor.execute('''SELECT auth_address FROM summaries WHERE date=?''',
                   (str(date),))
    address_list = cursor.fetchall()
    for address in address_list:
        address = ''.join(address)
        cursor.execute('''SELECT auth_address, uptime, duration, height FROM summaries
                       WHERE auth_address = ? AND date = ?''',
                       (str(address), str(date),))
        data = cursor.fetchone()
        address = data[0]
        uptime = data[1]
        duration = data[2]
        size = data[3]
        if duration == 0:
            points = 0
        else:
            points = (payments.height_function(size / 199999) *
                  payments.uptime_logistic_function(uptime/duration) *
                  (duration / 86400))
        cursor.execute('UPDATE summaries SET points = ? WHERE auth_address = ?'
                       'AND date = ?', (points, str(address), str(date),))
        conn.commit()


def assign_percentages(conn, cursor, date):
    """
    Assigns the percentage of the rewards that each build (authentication
    address) should receive on the specified date.
    """
    cursor.execute('SELECT sum(points) FROM summaries WHERE date=?', (str(date),))
    data = cursor.fetchone()
    total_points = data[0]
    cursor.execute('UPDATE summaries SET percentage = (points / ?) WHERE date=?',
                   (total_points, str(date),))
    conn.commit()


def begin_date(farmers_collection): # pragma: no cover
    """Returns the first date in the collection"""
    for doc in farmers_collection.find({}, {'time': 1, '_id': 0}
                                       ).sort('time', 1).limit(1):
        begin_date = doc['time']
    year = begin_date.year
    month = begin_date.month
    day = begin_date.day
    begin_date = dt.datetime(year, month, day, 0, 0, 0, 0)
    return begin_date


def end_date(farmers_collection): # pragma: no cover
    """Returns the last date in the collection"""
    for doc in farmers_collection.find({}, {'time': 1, '_id': 0}
                                       ).sort('time', -1).limit(1):
        end_date = doc['time']
    year = end_date.year
    month = end_date.month
    day = end_date.day
    last_date = dt.datetime(year, month, day, 0, 0, 0, 0)
    return last_date

