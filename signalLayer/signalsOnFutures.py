import pandas as pd

class signals:
    def __init__(self, indicators, options_data, lower_limit, upper_limit, window):
        self.trading_signal = pd.DataFrame()
        self.indicators = indicators
        self.options_data = options_data
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
    
    def simple_moving_average(self, ohlc_data, window=20):
        """
        Calculate simple moving average (SMA) and generate signals based on it.
        
        Parameters:
        - ohlc_data (DataFrame): DataFrame with OHLC data, indexed by timestamps.
        - window (int): Window period for SMA calculation.
        
        Returns:
        - DataFrame: DataFrame with 'entry_signal' and 'exit_signal' columns.
        """
        signals = pd.DataFrame(index=ohlc_data.index)
        signals['SMA'] = ohlc_data['close'].rolling(window=window).mean()
        signals['entry_signal'] = ohlc_data['close'] > signals['SMA']
        signals['exit_signal'] = ohlc_data['close'] < signals['SMA']
        return signals.astype(int)  # Convert boolean to 0s and 1s
    
    def relative_strength_index(self, ohlc_data, window=14):
        """
        Calculate Relative Strength Index (RSI) and generate signals based on it.
        
        Parameters:
        - ohlc_data (DataFrame): DataFrame with OHLC data, indexed by timestamps.
        - window (int): Window period for RSI calculation.
        
        Returns:
        - DataFrame: DataFrame with 'entry_signal' and 'exit_signal' columns.
        """
        signals = pd.DataFrame(index=ohlc_data.index)
        delta = ohlc_data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        signals['RSI'] = rsi
        signals['entry_signal'] = (signals['RSI'] < 30)
        signals['exit_signal'] = (signals['RSI'] > 70)
        return signals[['entry_signal', 'exit_signal']]

    def four_tags(self, tag1, tag2, tag3, tag4):
        
        self.trading_signal[tag1] = self.indicators[tag1]
        self.trading_signal[tag2] = self.indicators[tag2]
        self.trading_signal[tag3] = self.indicators[tag3]
        self.trading_signal[tag4] = self.indicators[tag4]
        self.trading_signal.dropna(inplace=True)
        
        self.trading_signal['long_signal_entry'] = self.trading_signal.apply(
        lambda x: x[tag1] < self.lower_limit and
                  x[tag2] < self.lower_limit and
                  x[tag3] < self.lower_limit and
                  x[tag4] < self.lower_limit,
        axis=1
    )
        self.trading_signal['short_signal_entry'] = self.trading_signal.apply(
        lambda x: x[tag1] > self.upper_limit and
                  x[tag2] > self.upper_limit and
                  x[tag3] > self.upper_limit and
                  x[tag4] > self.upper_limit,
        axis=1
    )
        self.trading_signal['long_signal_exit'] = False
        self.trading_signal['short_signal_exit'] = False
        
        return self.trading_signal