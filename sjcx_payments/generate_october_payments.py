#!/usr/local/bin/python3

# Script used to generate payments for October 2015.
# Creates the sqlite db and initializes it with previous payments.
import sqlite3
from pymongo import MongoClient
import payments
import datetime as dt

if __name__ == "__main__":
    conn = sqlite3.connect('rewards.db')
    cursor = conn.cursor()

    client = MongoClient('localhost', 27017)
    collection = client['GroupB']['farmers']


    d1 = dt.datetime(2015, 10, 1, 0, 0, 0)
    d2 = dt.datetime(2015, 11, 1, 0, 0, 0)

    payments.create_table(conn, cursor)
    payments.add_reward_stats(conn, cursor, collection, d1, d2)
    payments.add_payout_address(conn, cursor, collection)
    payments.add_balances(conn, cursor, d2)
    payments.assign_points(conn, cursor, d2)
    payments.distribute_sjcx(conn, cursor, d2)
    payments.init_past_rewards(conn, cursor)

    payments.make_points_csv(cursor, d2)