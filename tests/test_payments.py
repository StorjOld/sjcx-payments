import unittest
import datetime as dt
import sqlite3
from pymongo import MongoClient
import sjcx_payments.payments as payments
import os


class Payments(unittest.TestCase):

    def test_distinct_farmers(self):
        client = MongoClient('localhost', 27017)
        collection = client['GroupB']['farmers']
        test_d1 = dt.datetime(2015, 11, 14, 0, 0, 0)
        test_d2 = dt.datetime(2015, 11, 16, 0, 0, 0)
        farmers = payments.distinct_farmers(collection, test_d1, test_d2)
        self.assertTrue(len(farmers) > 0)
        self.assertTrue("1H6HBTUCVpZMLBqSUgrb9bZHnPTE4uSiKV" in farmers)

    def test_average_height(self):
        client = MongoClient('localhost', 27017)
        collection = client['GroupB']['farmers']
        test_d1 = dt.datetime(2015, 11, 14, 0, 0, 0)
        test_d2 = dt.datetime(2015, 11, 16, 0, 0, 0)
        test_btc_addr = "1H6HBTUCVpZMLBqSUgrb9bZHnPTE4uSiKV"
        height = payments.average_height(test_btc_addr, test_d1, test_d2, collection)
        self.assertTrue(height > 0)

    def test_add_reward_stats(self):
        client = MongoClient('localhost', 27017)
        collection = client['GroupB']['farmers']
        conn = sqlite3.connect('data/test_rewards.db')
        cursor = conn.cursor()
        test_d1 = dt.datetime(2015, 11, 14, 0, 0, 0)
        test_d2 = dt.datetime(2015, 11, 16, 0, 0, 0)
        payments.add_reward_stats(conn, cursor, collection, test_d1, test_d2)
        test_addr = "1H6HBTUCVpZMLBqSUgrb9bZHnPTE4uSiKV"
        cursor.execute('SELECT * FROM rewards WHERE auth_address = ? AND payment_date = ?',
                       (str(test_addr), str(test_d2),))
        data = cursor.fetchall()
        self.assertTrue(len(data) > 0)

    def test_add_payout_address(self):
        client = MongoClient('localhost', 27017)
        collection = client['GroupB']['farmers']
        conn = sqlite3.connect('data/test_rewards.db')
        cursor = conn.cursor()
        payments.add_payout_address(conn, cursor, collection)
        test_btc_addr = '1PxAH3dstbxW2WLSGahnLfC5w5JfEmBEad'
        cursor.execute('SELECT payout_address FROM rewards WHERE auth_address = ?',
                       (str(test_btc_addr),))
        data = cursor.fetchall()
        self.assertTrue(len(data) > 0)

    def test_add_balances(self):
        conn = sqlite3.connect('data/test_rewards.db')
        cursor = conn.cursor()
        test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
        payments.add_balances(conn, cursor, test_date)
        cursor.execute('''SELECT MAX(balance) FROM rewards WHERE payment_date=?''',
                       (str(test_date),))
        max_balance =cursor.fetchone()[0]
        self.assertTrue(max_balance > 0)
        conn.close()

    def test_assign_points(self):
        conn = sqlite3.connect('data/test_rewards.db')
        cursor = conn.cursor()
        test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
        payments.assign_points(conn, cursor, test_date)
        cursor.execute('''SELECT MAX(points) FROM rewards WHERE payment_date=?''',
                       (str(test_date),))
        points = cursor.fetchone()[0]
        self.assertTrue(points > 0)
        conn.close()

    def test_create_table(self):
        conn = sqlite3.connect('unittest.db')
        cursor = conn.cursor()
        payments.create_table(conn, cursor)
        dir = os.path.abspath('unittest.db')
        boolean = os.path.exists(dir)
        self.assertTrue(boolean)

    def test_distribute_sjcx(self):
        conn = sqlite3.connect('data/test_rewards.db')
        cursor = conn.cursor()
        test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
        payments.distribute_sjcx(conn, cursor, test_date)
        cursor.execute('''SELECT SUM(sjcx_reward) FROM rewards WHERE
                          payment_date = ?''', (str(test_date),))
        total = cursor.fetchone()[0]
        self.assertAlmostEqual(total, 100000)
        conn.close()

    def test_update_total_rewards(self):
        conn = sqlite3.connect('data/test_rewards.db')
        cursor = conn.cursor()
        test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
        payments.update_total_rewards(conn, cursor, test_date)
        cursor.execute('''SELECT MAX(total_usd_reward) FROM rewards WHERE
                          payment_date = ?''', (str(test_date),))
        usd_reward = cursor.fetchone()[0]
        self.assertTrue(usd_reward > 0)
        cursor.execute('''UPDATE rewards SET balance = 0, sjcx_reward = 0,
                          points = 0, usd_reward = 0, total_usd_reward = 0''')
        conn.commit()

    def test_make_csv(self):
        conn = sqlite3.connect('data/test_rewards.db')
        cursor = conn.cursor()
        test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
        payments.make_points_csv(cursor, test_date)
        dir = os.path.abspath('sjcx_rewards_2015_11_1.csv')
        boolean = os.path.exists(dir)
        self.assertTrue(boolean)

    def test_create_whitelist(self):
        whitelist = payments.create_whitelist()
        self.assertTrue(len(whitelist) > 0)

    def test_uptime_logistic_function(self):
        uptime = 0.5
        value = payments.uptime_logistic_function(uptime)
        self.assertTrue(isinstance(value, float))

    def test_height_function(self):
        height = 0.5
        value = payments.height_function(height)
        self.assertTrue(isinstance(value, float))

if __name__ == '__main__':
    unittest.main()
