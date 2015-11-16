import unittest
import sqlite3
from pymongo import MongoClient
import datetime as dt
import sjcx_payments.farmersummary as summary


class Summaries(unittest.TestCase):

    def test_init_table(self):
        conn = sqlite3.connect('data/test_summary.db')
        cursor = conn.cursor()
        client = MongoClient('localhost', 27017)
        collection = client['GroupB']['farmers']
        summary.init_table(conn, cursor, collection)
        cursor.execute('SELECT * FROM summaries')
        data = cursor.fetchall()
        self.assertTrue(len(data) > 0)
        test_addr = '1H6HBTUCVpZMLBqSUgrb9bZHnPTE4uSiKV'
        test_date = dt.datetime(2015, 11, 14, 0, 0, 0)
        cursor.execute('SELECT uptime, duration, height, points, percentage FROM summaries WHERE '
                       'auth_address = ? AND date = ?', (str(test_addr), str(test_date),))
        data = cursor.fetchone()
        uptime = data[0]
        duration = data[1]
        height = data[2]
        points = data[3]
        percentage = data[4]
        self.assertTrue(uptime > 0)
        self.assertTrue(duration > 0)
        self.assertTrue(height > 0)
        self.assertTrue(points > 0)
        self.assertTrue(percentage > 0)


