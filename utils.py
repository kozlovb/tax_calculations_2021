#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta

def parse_to_date(line):
    x = line.split()
    year_month_day = x[0].split("-")
    hour_min_sec = x[1].split(":")
    # datetime(year, month, day, hour, minute, second, microsecond)
    return datetime(int(year_month_day[0]), int(year_month_day[1]), int(year_month_day[2]), int(hour_min_sec[0]), int(hour_min_sec[1]), int(hour_min_sec[2]))

def read_prices(filename):
    file2 = open(filename, 'r')
    prices = file2.readlines()
    price_info = []
    for p in prices:
        price_info.append(p.split(','))
    return price_info

def amount_to_sell(register_info, date_to_sell):
    amount_to_sell = 0
    for r in register_info:
        if date_to_sell > r[1] + timedelta(days = 366):
            amount_to_sell += r[0]
    print("Amount_to_sell", amount_to_sell)
