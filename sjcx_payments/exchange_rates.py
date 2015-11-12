#!/usr/local/bin/python3
import requests
import time
import csv
from urllib.request import urlopen
from io import TextIOWrapper


SECONDS_IN_DAY = 86400
BTC_USD_URL = ("https://api.bitcoinaverage.com/history/USD/"
               "per_day_all_time_history.csv")


def btc_sjcx_rate(datetime):
    """
    Returns the btc to sjcx weighted average for the 24 hour
    period before the datetime.

    Args:
        datetime: date

    Returns:
        btc_sjcx_rate: value of 1 sjcx in bitcoins
    """
    end_timestamp = int(time.mktime(datetime.timetuple()))
    start_timestamp = end_timestamp - SECONDS_IN_DAY     #86400 seconds/day
    url = ("https://poloniex.com/public?command=returnChartData&currencyPair="
           "BTC_SJCX&start={}&end={}&period={}".format(start_timestamp,
                                                       end_timestamp,
                                                       SECONDS_IN_DAY))
    response = requests.get(url)
    rate = response.json()[0]["weightedAverage"]
    return rate


def btc_usd_rate(datetime):
    """
    Returns the btc to usd rate for the specified datetime.

    Args:
        datetime: date

    Returns:
        btc_usd_rate: value of 1 bitcoin in US dollars
    """
    response = urlopen(BTC_USD_URL)
    data = csv.reader(TextIOWrapper(response))
    for row in data:
        if row[0] == str(datetime):
            return float(row[3])


