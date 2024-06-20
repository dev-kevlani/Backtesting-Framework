from strategyLayer.createLegs import *
from strategyLayer.positionClass import *
from strategyLayer.strategyClass import *
from executionLayer.spreadStrategiesBacktester import *
from dataLayer.dataHandler import *
from reportingLayer.process_results import *
from signalLayer.signalsOnFutures import *
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
    end_date = datetime(2023, 1, 3)
    date_list = pd.date_range(start=start_date, end=end_date).to_pydatetime().tolist()
    sl_percentage_based = False
    tp_percentage_based = False
    
    sl = 1.25 if sl_percentage_based else 33
    tp = 0.7 if tp_percentage_based else 20
    
    strategy_type = ['directional', 'spread']
    
    instruments_with_actions = {
    'directional': {
        'long': [
            {'strike_part': 0, 'option_type': 'CE', 'action': 'buy', 'lots': 1},
            {'strike_part': 0, 'option_type': 'PE', 'action': 'sell', 'lots': 1}
        ],
        'short': [
            {'strike_part': 0, 'option_type': 'PE', 'action': 'buy', 'lots': 1},
            {'strike_part': 0, 'option_type': 'CE', 'action': 'sell', 'lots': 1}
        ]
    },
    'spread': [
        {'strike_part': 0, 'option_type': 'CE', 'action': 'sell', 'lots': 1},
        {'strike_part': 0, 'option_type': 'PE', 'action': 'sell', 'lots': 1},
        {'strike_part': +100, 'option_type': 'CE', 'action': 'sell', 'lots': 1},
        {'strike_part': -100, 'option_type': 'PE', 'action': 'sell', 'lots': 1},
        {'strike_part': +200, 'option_type': 'CE', 'action': 'buy', 'lots': 2},
        {'strike_part': -200, 'option_type': 'PE', 'action': 'buy', 'lots': 2}
    ]
}


    
    with multiprocessing.Pool(processes=32) as pool:
        data_handler = DataHandler('BANKNIFTY', timeframe='1T')
        results = pool.map(data_handler.fetch_and_process_data, [(date, sl, tp, instruments_with_actions, sl_percentage_based, tp_percentage_based, strategy_type[0]) for date in date_list])
    print(results)
    df_combined = process_results(results)
    visualizeAndSave(df_combined)
    
    return df_combined, results

if __name__ == '__main__':
    freeze_support()
    start_time = time.time()
    df_combined, results = run_backtesting()
    end_time = time.time()
    df_combined.to_csv("playing.csv")
    total_elapsed_time = end_time - start_time
    print(f"Backtesting completed in {total_elapsed_time:.2f} seconds")