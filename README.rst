========================
SJCX Payments Calculator
========================
sjcx-payments is used for calculating the sjcx rewards for the farmers on the Storj network. sjcx-payments uses farmer data stored in a MongoDB (data is collected by scrapers). Scrapers are in the driveshare-graph repository. 


Setup
=====
OSX
---
Install required packages
::
	$ brew install python3
	$ pip3 install -r requirements.txt

Ubuntu
------
Install required packages
::
	$ apt-get install python3 python3-pip
	$ pip3 install -r requirements.txt 


Command Line Usage
================== 

::
	$ python3 payments.py 
	  Enter the first date for the payment duration period in YYYY-MM-DD format. 2015-11-01
	  Enter the last date for the payment duration period in YYYY-MM-DD format. 2015-11-15
	  Calculating rewards...
	  Open sjcx_rewards.csv to see rewards

Payment Formula
===============
Current formula that is used to calculate sjcx rewards. 

* For each farmer/build (authentication address) who has a sjcx balance equal to or above 10,000 in their payout_address, calculate his/her points.
	* points = f(u) * g(h) * (duration/payment_period) 
		* u = uptime percentage (between 0 and 1)
		* h = height / max_height (max height is 199,999 for Test Group B)
		* f(x) is a logistic regression function 
		* g(x) = 0.01 + 0.99 * x
* Find the sum of the calculated points for all of the farmers. 
* Divide each farmer's points by the sum in order to get the percentage of rewards that the farmer should receive. Multiply that percentage by the total rewards pool. 

Changing the formula
--------------------
All components of the farmula are in payments.py. If the total rewards pool, payment period, or max height changes,change the value of the global variables, SJCX_TOTAL_REWARDS and INDIVIDUAL_MAX_HEIGHT. Current code assumes a 2 week payment period. 


