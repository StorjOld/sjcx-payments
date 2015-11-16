========================
SJCX Payments Calculator
========================

|BuildLink|_ |CoverageLink|_ |LicenseLink|_ 


.. |BuildLink| image:: https://travis-ci.org/Storj/sjcx-payments.svg?branch=master
.. _BuildLink: https://travis-ci.org/Storj/sjcx-payments

.. |CoverageLink| image:: https://coveralls.io/repos/Storj/sjcx-payments/badge.svg?branch=master&service=github
.. _CoverageLink: https://coveralls.io/github/Storj/sjcx-payments?branch=master

.. |LicenseLink| image:: https://img.shields.io/badge/license-MIT-blue.svg
.. _LicenseLink: https://raw.githubusercontent.com/Storj/sjcx-payments

sjcx-payments is used for calculating the sjcx rewards for the farmers on the Storj network. sjcx-payments uses farmer data stored in a MongoDB (data is collected by scrapers). Scrapers are in the driveshare-graph repository.  


Setup
=====

OSX
---
Install required packages
::
	$ git clone https://github.com/Storj/sjcx-payments.git
	$ cd sjcx-payments
	$ brew install python3 sqlite3
	$ pip3 install -r requirements.txt

Ubuntu
------
Install required packages
::
	$ git clone https://github.com/Storj/sjcx-payments.git
	$ cd sjcx-payments
	$ sudo apt-get install python3 python3-pip sqlite3 libsqlite3-dev
	$ pip3 install -r requirements.txt 


Command Line Usage
================== 

Run this script on a machine that stores the MongoDB data from the driveshare-graph scrapers. This is essential because payments.py uses the data from the MongoDB to calculate farmer statistics (duration, uptime, height). 

Example usage
::
	$ cd sjcx_payments
	$ python3 payments.py 
	  Enter the first date for the payment duration period in YYYY-MM-DD format. 2015-11-01
	  Enter the last date for the payment duration period in YYYY-MM-DD format. 2015-11-15
	  Calculating rewards...
	  Open sjcx_rewards.csv to see rewards

Running this script would add the farmer stats/rewards for the period (11/1/2015 - 11/15/2015) into rewards.db (located in data directory). 


Payment Formula
===============

Current formula that is used to calculate sjcx rewards. 

* For each farmer/build (authentication address) who has a sjcx balance equal to or above 10,000 in their payout_address, calculate his/her points.
	* points = f(u) * g(h) * (duration/payment_period) 
		* u = uptime percentage (between 0 and 1)
		* h = height / max_height (max height is 199,999 for Test Group B)
		* f(x) is a logistic regression function 
		* g(x) = 0.01 + 0.99 * x
	* If the build has a payout address with a balance below 10,000 sjcx and the payout address is on the whitelist, multiply their points value by balance / 10,000. Builds with balances below 10,000 sjcx and not on the whitelist get zero points. 
* Find the sum of the calculated points for all of the farmers. 
* Divide each farmer's points by the sum in order to get the percentage of rewards that the farmer should receive. Multiply that percentage by the total rewards pool. 

Changing the formula
--------------------
All components of the formula are in payments.py. If the total rewards pool, payment period, or max height changes,change the value of the global variables, SJCX_TOTAL_REWARDS and INDIVIDUAL_MAX_HEIGHT. Current code assumes a 2 week payment period. 

Summaries
=========
farmersummary.py contains the functions needed to create and update a sqlite summaries table. It uses the MongoDB farmers collection to produce daily summaries (uptime, height, duration, points, percentage of total points for each build--authentication adddress). 

Example usage in ipython3
::
	import farmersummary
	import sqlite3
	from pymongo import MongoClient
	
	conn = sqlite3.connect('summary.db')
	cursor = conn.cursor()
	client = MongoClient('localhost', 27017)
	collection = client['GroupB']['farmers']
	
	# To create and initialize table
	farmersummary.create_summary_table(conn, cursor)
	farmersummary.init_table(conn, cursor, collection)
	
	# To update payments 
	farmersummary.update_table(conn, cursor, collection)

To search for specific farmer summaries, simply query the summary.db. You can also use an application like SQLiteBrowser to look through the database contents. 

Data
==== 

The data folder includes "Storj Test Group B Rewards complicance.xlsx" and rewards.db. The excel file contains the first three payout information. rewards.db is a sqlite database. rewards.db contains the payment history and farmer stats for the October 2015 (10/1/2015-10/31/2015) payment batch. Executing payments.py adds the payment stats for that period into rewards.db. 


