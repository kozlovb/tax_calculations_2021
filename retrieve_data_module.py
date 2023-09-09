#!/usr/bin/env python

# Kraken Historical Time and Sales
# Usage: ./krakenhistory symbol start [end]
# Example: ./krakenhistory XXBTZUSD 1559347200 1559433600

import sys
import time
import urllib.request
import json
import statistics

api_domain = "https://api.kraken.com"
api_path = "/0/public/"
api_method = "Trades"
api_data = ""
api_symbol = "XXBTZEUR"


def request_price_online(start_time):
    sleep = True
    api_start = str(int(start_time) - 1 - 15) + "999999999"
    api_end = start_time + 15
    average = []
    GReatSuccess = False
    while not GReatSuccess:
        api_data = "?pair=%(pair)s&since=%(since)s" % {"pair":api_symbol, "since":api_start}
        api_request = urllib.request.Request(api_domain + api_path + api_method + api_data)
        print("REQUEST", api_domain + api_path + api_method + api_data)
        for i in range(10):
            passed = True
            try:
                api_data = urllib.request.urlopen(api_request).read()
                api_data = json.loads(api_data)
                if len(api_data["error"]) != 0:
                    print("ERROR in api_data")
                    raise Exception("error")
                passed = True
            except Exception:
                time.sleep(20)
                passed = False
            if passed:
                break
            if i == 9:
                print("WARNING 9th execution")
        for trade in api_data["result"][api_symbol]:
            print("Trade", trade)
            print("Time of trade", trade[2], "Time of api_end", int(api_end))
            if int(trade[2]) < int(api_end):
                #print("%(datetime)d,%(price)s,%(volume)s" % {"datetime":trade[2], "price":trade[0], "volume":trade[1]})
                average.append(float(trade[0]))
            else:
                if average:
                    GReatSuccess = True
                    return statistics.mean(average)
                else:
                    print("Got out of range delta ", trade[2] - int(api_end))
                    return float(trade[0])
