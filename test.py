import pytest
from tax_futures import *

SECONDS_IN_YEAR = 31536000 

def test_update_state(kraken_logs, state):
    taxable_early_sell = state.process(kraken_logs)
    assert taxable_early_sell == 10


#
state = State()
kraken_logs = KrakenLogs()
kraken_logs()

state.state.append(StateEntry(1, 10000, 1000))
state.state.append(StateEntry(1, 20000, 1000))
state.state.append(StateEntry(1, 10000, 1000))