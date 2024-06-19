from strategyLayer.createLegs import *
from strategyLayer.positionClass import *
from strategyLayer.strategyClass import *
from executionLayer.spreadStrategiesBacktester import *
from dataLayer.dataHandler import *
from reportingLayer.process_results import *
import pandas as pd
from datetime import datetime
import multiprocessing
from multiprocessing import freeze_support
import time
import gc
import warnings

warnings.filterwarnings("ignore")

gc.collect()

def run_backtesting():
    
    tickers = ['BANKNIFTY', 'NIFTY']
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    date_list = pd.date_range(start=start_date, end=end_date).to_pydatetime().tolist()
    sl_percentage_based = False  # Change this flag based on your requirement
    tp_percentage_based = False  # Change this flag based on your requirement
    
    sl = 1.25 if sl_percentage_based else 15  # Example values, adjust as needed
    tp = 0.7 if tp_percentage_based else 15  # Example values, adjust as needed
    instruments_with_actions = [
        {
            'strike_part': +200,
            'option_type': 'CE',
            'action': 'sell'
        },
        {
            'strike_part': -200,
            'option_type': 'PE',
            'action': 'sell'
        },
        {
            'strike_part': +300,
            'option_type': 'CE',
            'action': 'sell'
        },
        {
            'strike_part': -300,
            'option_type': 'PE',
            'action': 'sell'
        },
        {
            'strike_part': +400,
            'option_type': 'CE',
            'action': 'buy'
        },
        {
            'strike_part': -400,
            'option_type': 'PE',
            'action': 'buy'
        }
    ]
    
    with multiprocessing.Pool(processes=32) as pool:
        data_handler = DataHandler('BANKNIFTY', timeframe='1T')
        results = pool.map(data_handler.fetch_and_process_data, [(date, sl, tp, instruments_with_actions, sl_percentage_based, tp_percentage_based) for date in date_list])
        
    df_combined = process_results(results)
    visualizeAndSave(df_combined)
    
    return df_combined, results

if __name__ == '__main__':
    freeze_support()
    start_time = time.time()
    df_combined, results = run_backtesting()
    end_time = time.time()
    
    total_elapsed_time = end_time - start_time
    print(f"Backtesting completed in {total_elapsed_time:.2f} seconds")