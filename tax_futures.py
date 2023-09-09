#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
from retrieve_data_module import *
from utils import *

#0   1        2       3    4      5      6           7                       8           9          10           11           12  13               14    
#uid,dateTime,account,type,symbol,change,new balance,new average entry price,trade price,mark price,funding rate,realized pnl,fee,realized funding,collateral
# we are interested only in 1- dateTime, 11-realized pnl, 12 - fee.
class KrakenLogEntry:
    def __init__(self, uid, since_epoch, realized_pnl, fee):
        self.uid = uid
        self.since_epoch = since_epoch
        self.realized_pnl = realized_pnl
        self.fee = fee

# class that reads KrakenLogs
class KrakenLogs:
    def __init__(self,filename):
        self.kraken_trades = [] 
        if filename:
            self.read_kraken_logs(filename)   

    def read_kraken_logs(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()
            for l in lines:
                fields = l.split(',')
                if fields[2] == 'f-xbt:usd' and fields[3] == 'futures trade' and fields[4] == 'xbt':
                    self.kraken_trades.append(KrakenLogEntry(fields[0], parse_to_date(fields[1]).timestamp(), float(fields[11]), float(fields[12])))
            self.kraken_trades.reverse()
     
class ReportEntry:
    def __init__(self, profit, loss, fee):
        self.profit = profit
        self.loss = loss
        self.fee = fee  

# This report is not related o early sell but purely for
# Kraken trades themsselves  
class ReportOnKrakenTrades:
    def __init__(self, kraken_log):
        self.kraken_log = kraken_log
        
    def generate_report(self, price_filename):
        price_info = read_prices(price_filename)
        eur_report = ReportEntry(0,0,0)
        btc_report = ReportEntry(0,0,0)
        for trade in self.kraken_log.kraken_trades:
            price = determine_price(trade.uid, trade.since_epoch, price_info)
            if float(trade.realized_pnl) > 0:
                btc_report.profit += float(trade.realized_pnl)
                eur_report.profit += float(trade.realized_pnl)*price
            else:
                btc_report.loss += float(trade.realized_pnl)
                eur_report.loss += float(trade.realized_pnl)*price
            btc_report.fee += float(trade.fee)
            eur_report.fee += float(trade.fee)*price
        return btc_report, eur_report

# A state entry consists of quantity, time in seconds since epoch and price
class StateEntry:
    def __init__(self, qty, time_epoch, price):
        self.qty = qty
        self.time_epoch = time_epoch
        self.price = price

class State:
    def __init__(self, state_filename):
        self.state = []
        if state_filename:
            self.read_state(state_filename)

    def read_state(self, state_filename):
        with open(state_filename,"r") as file:
            register_lines = file.readlines()
            for r in register_lines:
                register_fields = r.split(",")
                #qty time price
                self.state.append(StateEntry(float(register_fields[1]), float(register_fields[2]), float(register_fields[3])))

    def update_state_with_trade(self, amount, time_since_ep, price, fee):
        if amount > 0:
            return self.update_state_win(amount, time_since_ep, price, fee)
        else:
            return self.update_state_loss(-amount, time_since_ep, price, fee)

    def update_state_win(self, amount, since_ep, price, fee):
        # fee is treated like a loss and has to be substracted from the register
        taxable = self.update_state_loss(0, since_ep, price, fee)
        # otherwise a gained crypto is jusst appended
        self.state.append(StateEntry(amount, since_ep, price))
        return taxable

    def update_state_loss(self, amount, since_ep, price, fee):
        new_state = []
        taxable = 0
        amount += fee
        for r in self.state:
            if amount == 0:
                new_state.append(r)
            elif amount > r.qty:
                amount = amount - r.qty
                if datetime.fromtimestamp(r.time_epoch) + timedelta(days = 365) > datetime.fromtimestamp(since_ep):
                    taxable += r.qty*(price - r.price)
            elif amount > 0 and amount < r.qty:
                new_state.append(StateEntry(r.qty - amount, r.time_epoch, r.price))
                if datetime.fromtimestamp(r.time_epoch) + timedelta(days = 366) > datetime.fromtimestamp(since_ep):
                    taxable += amount*(price - r.price)
                amount = 0
        self.state = new_state
        return taxable

    def process(self, kraken_logs, price_filename):
        taxable_early_sell = 0
        price_info = read_prices(price_filename)
        one_time_sold_btc_treated = False
        for kraken_log in kraken_logs.kraken_trades:
            if 1626210760 < kraken_log.since_epoch and not one_time_sold_btc_treated:
                #the fee for this trade is 408 euro and can be substrated from the gain. 
                taxable_delta = self.update_state_with_trade(-1.0, 1626210760, 27643, 0)
                taxable_early_sell += taxable_delta - 408
                one_time_sold_btc_treated = True
            price = determine_price(kraken_log.uid, kraken_log.since_epoch, price_info)
            taxable_delta = self.update_state_with_trade(kraken_log.realized_pnl, kraken_log.since_epoch, price, kraken_log.fee) 
            taxable_early_sell += taxable_delta
        return taxable_early_sell

    def save(self, filename):
        with open(filename, "w") as f:
            old_timestamp = self.state[0].time_epoch
            for r in self.state:
                new_timestamp = r.time_epoch
                if new_timestamp < old_timestamp:
                    print("ERROR in register timestamp")
                    exit()
                old_timestamp = new_timestamp
                f.write(str(r.qty) + "," + str(r.time_epoch) + "," + str(r.price)+ "\n")
      
def determine_price(trade_id, since_ep_date, price_info):
    for p in price_info:
        if p[0] == trade_id:
            return float(p[2])
    price = request_price_online(since_ep_date)
    return float(price)

if __name__ == "__main__":
    #Execution
    state = State("register.txt")
    kraken_logs = KrakenLogs("kraken_log.txt")

    taxable_early_sell = state.process(kraken_logs, "price.txt")

    state.save("new_register.txt")

    print("Taxes from early sell", taxable_early_sell)

    report = ReportOnKrakenTrades(kraken_logs)
    btc_report , eur_report = report.generate_report("price.txt")

    print("btc_profit", btc_report.profit, "btc_loss", btc_report.loss, "btc_fee", btc_report.fee)
    print("eur_profit", eur_report.profit, "eur_loss", eur_report.loss, "eur_fee", eur_report.fee)