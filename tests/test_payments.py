import unittest
import datetime as dt
import sqlite3
import sjcx_payments.payments as payments


class Payments(unittest.TestCase):

    # def test_assign_points(self):
    #     test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
    #     conn = sqlite3.connect('data/test_rewards.db')
    #     cursor = conn.cursor()
    #     payments.assign_points(conn, cursor, test_date)
    #     cursor.execute('''SELECT MAX(points) FROM rewards WHERE payment_date=?''',
    #                    (str(test_date),))
    #     points = cursor.fetchone()[0]
    #     self.assertTrue(points > 0)


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
