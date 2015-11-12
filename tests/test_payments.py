import unittest
import datetime as dt
import sqlite3
import sjcx_payments.payments as payments


class Payments(unittest.TestCase):

    def setup(self):
        self.conn = sqlite3.connect('data/test_rewards.db')
        self.cursor = self.conn.cursor()

    def test_add_balances(self):
        test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
        payments.add_balances(self.conn, self.cursor, test_date)
        self.cursor.execute('''SELECT MAX(balance) FROM rewards WHERE payment_date=?''',
                       (str(test_date),))
        max_balance = self.cursor.fetchone()[0]
        self.assertTrue(max_balance > 0)

    def test_assign_points(self):
        test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
        payments.assign_points(self.conn, self.cursor, test_date)
        self.cursor.execute('''SELECT MAX(points) FROM rewards WHERE payment_date=?''',
                       (str(test_date),))
        points = self.cursor.fetchone()[0]
        self.assertTrue(points > 0)

    def test_uptime_logistic_function(self):
        uptime = 0.5
        value = payments.uptime_logistic_function(uptime)
        self.assertTrue(isinstance(value, float))

    def test_height_function(self):
        height = 0.5
        value = payments.height_function(height)
        self.assertTrue(isinstance(value, float))

    def tearDown(self):
        self.cursor.execute('''UPDATE rewards SET balance = 0, points = 0,
                               sjcx_reward = 0, usd_reward = 0,
                               total_usd_reward = 0''')
        self.conn.commit()
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
