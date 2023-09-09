from tax_futures import *

SECONDS_IN_YEAR = 31536000 

def is_close(a, b,):
    return abs(a - b) <= 1e-08

def test_update_state1():
    state = State(None)
    kraken_logs = KrakenLogs(None)
    kraken_logs.kraken_trades.append(KrakenLogEntry("1", 21000, -1.5, 0.1))
    #price 40000

    kraken_logs.kraken_trades.append(KrakenLogEntry("2", 2 * SECONDS_IN_YEAR, -1, 0.1))
    #price 30000

                                #qty #time  #price     
    state.state.append(StateEntry(1, 10000, 1000))
    state.state.append(StateEntry(1, 20000, 2000))
    state.state.append(StateEntry(1, 30000, 1000))

    taxable_early_sell = state.process(kraken_logs, "price_test.txt")
    print(taxable_early_sell)
    # Calculate by hand:
    # 1 trade
    # -1.5 and fee 0.1 results in 1.6 btc spent
    # tax = 1 * (40000 - 1000) +  (0.6)*(40000-2000) = 61800
    # 2 trade
    # tax = 0
    assert taxable_early_sell == 61800

    #check state , should be 0.3btc 3000 1000 , 0.3 because 3-1.5-1-0.1-0.1
    assert len(state.state) == 1
    assert is_close(state.state[0].qty, 0.3) and state.state[0].time_epoch == 30000 and state.state[0].price == 1000
    print("test_update_state1 passed")

def test_update_state2():
    state = State(None)
    kraken_logs = KrakenLogs(None)
    kraken_logs.kraken_trades.append(KrakenLogEntry("1", 30001, 1.5, 0.5))
    #price 40000

                                #qty #time  #price     
    state.state.append(StateEntry(0.1, 10000, 1000))
    state.state.append(StateEntry(0.1, 2000,  50000))
    state.state.append(StateEntry(1  , 30000, 1000))

    taxable_early_sell = state.process(kraken_logs, "price_test.txt")
    print(taxable_early_sell)
    # Calculate by hand:
    # 1 trade
    # +1.5 and fee 0.5 results in 0.5 btc spent
    # tax = 0.1 * (40000 - 1000) + -0.1(50000-40000) (0.3)*(40000-1000) = 14600
    # 2 trade
    # tax = 0
    assert is_close(taxable_early_sell, 14600)

    #check state , should be 
    # 0.7 30000 1000
    # 1.5 30001 40000
    assert len(state.state) == 2
    assert is_close(state.state[0].qty, 0.7) and state.state[0].time_epoch == 30000 and state.state[0].price == 1000
    assert is_close(state.state[1].qty, 1.5) and state.state[1].time_epoch == 30001 and state.state[1].price == 40000
    print("test_update_state2 passed")

test_update_state1()
test_update_state2()

