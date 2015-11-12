import unittest
import datetime as dt
import sjcx_payments.payments as payments


class Payments(unittest.TestCase):

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

