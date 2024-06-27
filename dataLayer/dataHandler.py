import pandas as pd
from datetime import datetime, timedelta
from .dataFetching import get_option_data, get_futures_data
from .ohlcBuilder import create_ohlc_candles
from .applying_indicators import apply_indicators
from .calculateGreeks import calculate_iv_and_greeks
from strategyLayer.createLegs import *
from strategyLayer.positionClass import *
from strategyLayer.strategyClass import *
from executionLayer.spreadStrategiesBacktester import *
from signalLayer.signalsOnFutures import *
import time

class DataHandler:
    def __init__(self, ticker, timeframe):
        """
        Initialize DataHandler with ticker symbol and timeframe.

        Args:
        - ticker (str): Ticker symbol for the financial instrument (e.g., 'BANKNIFTY').
        - timeframe (str): Timeframe for OHLC data (e.g., '1T' for 1-minute intervals).
        """
        self.ticker = ticker
        self.timeframe = timeframe

    def process_data(self, date, futures_data, options_data, timeframe):
        """
        Process futures and options data for a given date.

        Args:
        - date (datetime): Date for which data is processed.
        - futures_data (DataFrame or None): Dataframe containing futures data for the specified date.
        - options_data (DataFrame or None): Dataframe containing options data for the specified date.
        - timeframe (str): Timeframe for OHLC data.

        Returns:
        - Tuple: Processed data including OHLC candles, RSI indicator, and processed options data.
        """
        if futures_data is None:
            options_data_processed = calculate_iv_and_greeks(options_data)
            return date, None, None, options_data_processed

        ohlc_data = create_ohlc_candles(futures_data, timeframe)
        indicator_data, indicator_rsi, indicator_stoch = apply_indicators(ohlc_data.copy())
        options_data_processed = calculate_iv_and_greeks(options_data)
        
        return date, ohlc_data, indicator_rsi, options_data_processed

    def fetch_data(self, date):
        """
        Fetch futures and options data for a given date and process it.

        Args:
        - date (datetime): Date for which data is fetched.

        Returns:
        - Tuple: Processed data from process_data method.
        """
        futures_data = get_futures_data(self.ticker, date.year, date.month, date.day)
        options_data = get_option_data(self.ticker, date.year, date.month, date.day)
        return self.process_data(date, futures_data, options_data, self.timeframe)

    def fetch_and_process_data(self, args):
        """
        Fetches and processes data for backtesting based on provided arguments.

        Args:
        - args (tuple): Tuple containing date, stop loss (sl), target profit (tp),
          instruments with actions, strategy type, and other parameters.

        Returns:
        - Tuple: Trades and uncounted trades generated during backtesting.
        """
        date, sl, tp, instruments_with_actions, sl_percentage_based, tp_percentage_based, strategy_type = args
        date, ohlc_data, indicator_data, options_data_processed = self.fetch_data(date)
        
        if options_data_processed is not None:
            if isinstance(options_data_processed, tuple):
                return None  # Return None if options_data_processed is not valid
            
            options_data_processed.index = pd.to_datetime(options_data_processed.index)
            
            signal_generator = signals(indicator_data, options_data_processed, 15, 95)
            signal_df = signal_generator.four_tags('ulcer_index_rsi', 'kc_low_rsi', 'kc_low_rsi', 'kc_low_rsi')
            
            if signal_df is None:
                return None  # Return None if no valid signals are generated
            
            signal_df = signal_generator.clean_signals(signal_df)
            
            # Initialize SpreadBacktester to execute backtesting
            backtester = SpreadBacktester(options_data_processed, signal_df, sl, tp, instruments_with_actions,
                                          sl_percentage_based, tp_percentage_based, strategy_type)
            start_time = time.time()
            starting_timestamp = backtester.classifying_signals()
            trades, uncounted_trades = backtester.execute_trades(starting_timestamp)
            end_time = time.time()
            
            elapsed_time = end_time - start_time
            print(f"Processed {date} in {elapsed_time:.2f} seconds")
            return trades, uncounted_trades
        else:
            return None  # Return None if options_data_processed is None
