import unittest
import datetime as dt
import sqlite3
import sjcx_payments.payments as payments
import os


class Payments(unittest.TestCase):

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

    # def test_make_csv(self):
    #     conn = sqlite3.connect('data/test_rewards.db')
    #     cursor = conn.cursor()
    #     test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
    #     payments.make_points_csv(cursor, test_date)
    #     dir = os.path.abspath('sjcx_rewards_2015_11_1.csv')
    #     boolean = os.path.exists(dir)
    #     self.assertTrue(boolean)
    #     cursor.execute('''UPDATE rewards SET balance = 0, sjcx_reward = 0,
    #                       points = 0, usd_reward = 0, total_usd_reward = 0''')
    #     conn.commit()

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
