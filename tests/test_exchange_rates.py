import unittest
import datetime as dt
import sjcx-payments.scripts.exchange_rates as exchange_rate
from datetime import timedelta

class ExchangeRates(unittest.TestCase):
    
    def test_btc_sjcx(self):
        date = dt.datetime.now() - timedelta(seconds = 86400)
        btc_sjcx = exchange_rate.btc_sjcx_rate(date)
        self.assertTrue(isinstance(btc_sjcx, float))

    def test_btc_usd(self):
	date = dt.datetime.now() - timedelta(seconds = 86400)
        prev_date = dt.datetime(date.year, date.month, date.day, 0, 0, 0)
        btc_usd = exchange_rate.btc_usd_rate(prev_date)
        self.assertTrue(isinstance(btc_usd, float))


