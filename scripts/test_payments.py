import unittest
import sqlite3
import datetime as dt
import scripts.payments as payments


class Payments(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect('../data/test_rewards.db')
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_assign_points(self):
        test_date = dt.datetime(2015, 11, 1, 0, 0, 0)
        payments.assign_points(self.conn, self.cursor, test_date)
        self.cursor.execute('''SELECT MAX(points) FROM rewards WHERE
                               payment_date = ?''', (str(date),))
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
        

