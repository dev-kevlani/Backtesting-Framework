import pandas as pd
from datetime import datetime
from dataFetching import get_option_data, get_futures_data
from ohlcBuilder import create_ohlc_candles
from applying_indicators import apply_indicators
from calculateGreeks import calculate_iv_and_greeks
import multiprocessing
from multiprocessing import freeze_support

class DataHandler:
    
    def __init__(self, ticker, start_date, end_date, timeframe):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = {}
        self.futures_ohlc_data = {}
        self.futures_indicator_data = {}
        self.options_data = {}
        self.options_mapped_dict = {}
        self.timeframe = timeframe
        self.date_list = pd.date_range(start=start_date, end=end_date).to_pydatetime().tolist()

    def process_data(self, date, futures_data, options_data, timeframe):
        if futures_data is None:
            return None, None, None, None

        ohlc_data = create_ohlc_candles(futures_data, timeframe)
        
        # if strategy_type in ['STRADDLE', 'STRANGLE', etc etc]:
        #     calculate_options_processed_data
            
        #     return that
        
        indicator_data = apply_indicators(ohlc_data.copy())
        options_data_processed = calculate_iv_and_greeks(options_data)
        
        return date, ohlc_data, indicator_data, options_data_processed


    def fetch_data(self, args):
        
        date = args
        futures_data = get_futures_data(self.ticker, date.year, date.month, date.day)
        options_data = get_option_data(self.ticker, date.year, date.month, date.day)
        date, ohlc_data, indicator_data, options_data_processed = self.process_data(date, futures_data, options_data, '1T')
        
        return date, ohlc_data, indicator_data, options_data_processed


    def fetch_and_process_data(self):
        
        with multiprocessing.Pool(processes=32) as pool:
            fetch_data = pool.map(self.fetch_data, [(date) for date in self.date_list])

        return fetch_data

if __name__ == '__main__':
    
    freeze_support()
    tickers = ['BANKNIFTY', 'NIFTY']
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    
    data_handler = DataHandler('BANKNIFTY', start_date, end_date, timeframe='1T')
    fetched_data = data_handler.fetch_and_process_data()
