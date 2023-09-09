#!/usr/bin/env python

# Kraken Historical Time and Sales
# Usage: ./krakenhistory symbol start [end]
# Example: ./krakenhistory XXBTZUSD 1559347200 1559433600

import sys
import time
import urllib.request
import json

api_domain = "https://api.kraken.com"
api_path = "/0/public/"
api_method = "Trades"
api_data = ""

if len(sys.argv) < 3:
	sys.exit(1)

api_symbol = sys.argv[1].upper()
api_start = str(int(sys.argv[2]) - 1) + "999999999"

if len(sys.argv) > 3:
	api_end = sys.argv[3]
else:
	api_end = "9999999999"

try:
	while True:
		api_data = "?pair=%(pair)s&since=%(since)s" % {"pair":api_symbol, "since":api_start}
		api_request = urllib.request.Request(api_domain + api_path + api_method + api_data)
		print('REQUEST', api_domain + api_path + api_method + api_data)
		try:
			api_data = urllib.request.urlopen(api_request).read()
		except Exception:
			time.sleep(3)
			continue
		api_data = json.loads(api_data)
		if len(api_data["error"]) != 0:
			time.sleep(3)
			continue
		for trade in api_data["result"][api_symbol]:
			if int(trade[2]) < int(api_end):
				print("%(datetime)d,%(price)s,%(volume)s" % {"datetime":trade[2], "price":trade[0], "volume":trade[1]})
			else:
				sys.exit(0)
		api_start = api_data["result"]["last"]
except KeyboardInterrupt:
	None

sys.exit(0)
