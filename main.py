# Import necessary libraries and modules
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

# Ignore warnings for cleaner output
warnings.filterwarnings("ignore")

# Perform garbage collection to free up memory
gc.collect()

# Define the function to run backtesting
def run_backtesting():
    # Define parameters for backtesting
    tickers = ['BANKNIFTY', 'NIFTY']
    start_date = datetime(2023, 1, 3)
    end_date = datetime(2023, 1, 31)
    date_list = pd.date_range(start=start_date, end=end_date).to_pydatetime().tolist()
    sl_percentage_based = True
    tp_percentage_based = True
    
    # Define stop loss and target profit based on percentage or fixed values
    sl = 1.1 if sl_percentage_based else 20
    tp = 0.8 if tp_percentage_based else 40
    
    # Define types of strategies to backtest
    strategy_type = ['directional', 'spread']
    
    # Define instruments and actions for each strategy type
    instruments_with_actions = {
        'directional': {
            'long': [
                {'strike_part': 0, 'option_type': 'CE', 'action': 'buy', 'lots': 1},
                # {'strike_part': 0, 'option_type': 'PE', 'action': 'sell', 'lots': 1}
            ],
            'short': [
                {'strike_part': 0, 'option_type': 'PE', 'action': 'buy', 'lots': 1},
                # {'strike_part': 0, 'option_type': 'CE', 'action': 'sell', 'lots': 1}
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
    
    # Initialize multiprocessing pool for parallel processing
    with multiprocessing.Pool(processes=32) as pool:
        # Initialize data handler for fetching and processing historical data
        data_handler = DataHandler('BANKNIFTY', timeframe='1T')
        # Map data handler function across dates to fetch and process data in parallel
        results = pool.map(data_handler.fetch_and_process_data, [(date, sl, tp, instruments_with_actions, sl_percentage_based, tp_percentage_based, strategy_type[0]) for date in date_list])
    
    # Process results from backtesting to get combined dataframe and metrics
    df_combined, total_trades, winning_trades, accuracy = process_results(results)
    print(f"Total Trades: {total_trades}, Winning Trades: {winning_trades}, Accuracy: {accuracy}")
    
    # Visualize and save results (visualization function assumed to be defined elsewhere)
    visualizeAndSave(df_combined)
    
    # Return combined dataframe and results
    return df_combined, results

# Main entry point of the script
if __name__ == '__main__':
    # Ensure multiprocessing compatibility on Windows
    freeze_support()
    
    # Record start time for measuring execution time
    start_time = time.time()
    
    # Execute the backtesting function
    df_combined, results = run_backtesting()
    
    # Record end time and calculate total elapsed time
    end_time = time.time()
    total_elapsed_time = end_time - start_time
    
    # Save combined dataframe to CSV for further analysis
    df_combined.to_csv("backtest_results.csv")
    
    # Print total elapsed time for the entire backtesting process
    print(f"Backtesting completed in {total_elapsed_time:.2f} seconds")
