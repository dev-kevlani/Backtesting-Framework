
from .indicatorLibrary import all_indicators

rolling_window_of_returns = 4
rsi_window = 4
bb_window = rolling_window_of_returns
bb_deviation = 2
atr_kc_multiplier = bb_deviation
donchian_window = rolling_window_of_returns
keltner_window = rolling_window_of_returns
keltner_window_atr = rolling_window_of_returns
ulcer_index_window = rolling_window_of_returns
atr_window = rolling_window_of_returns
chaikin_volatility_period = rolling_window_of_returns
dpo_period = rolling_window_of_returns
roc_period = rolling_window_of_returns
rvi_period = rolling_window_of_returns
gamma = 0.5
short_window = rolling_window_of_returns+1
medium_window = short_window*3
long_window = medium_window * 3
signal_window = medium_window
multiplier = bb_deviation
k_window = rolling_window_of_returns
d_window = rolling_window_of_returns
acceleration_psar = 0.05
maximum_psar = 0.5
window = rolling_window_of_returns

def apply_indicators(data):
    
    args = (data, rsi_window, gamma, window, short_window, medium_window, long_window, signal_window, k_window, d_window, \
            bb_window, bb_deviation, donchian_window, keltner_window,\
            ulcer_index_window, atr_window, chaikin_volatility_period, \
            atr_kc_multiplier, dpo_period, roc_period)
    
    ohlc_with_indicators, ohlc_with_indicators_rsi, ohlc_with_indicators_stoch = all_indicators(args)
    
    return ohlc_with_indicators, ohlc_with_indicators_rsi, ohlc_with_indicators_stoch