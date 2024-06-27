import pandas as pd

def get_option_data(ticker, year, month, day):
    """
    Retrieve options data from pickle files based on the ticker, year, month, and day.

    Parameters:
    - ticker (str): Ticker symbol ('BANKNIFTY' or 'NIFTY').
    - year (int): Year of the data.
    - month (int): Month of the data.
    - day (int): Day of the data.

    Returns:
    - data (pd.DataFrame or None): DataFrame containing options data if successful, None if unsuccessful.
    """
    try:
        if ticker == 'BANKNIFTY':
            data = pd.read_pickle(r"D:\BNFDATA\options_data_backtest\pickles\{}_{}_{}.pkl".format(day, month, year))
            if not data.empty:
                return data
            
        elif ticker == 'NIFTY':
            data = pd.read_pickle(r"D:\NIFTYDATA\options_data\pickles\{}_{}_{}.pkl".format(day, month, year))
            if not data.empty:
                return data
    except Exception as e:
        print(f"Error occurred while retrieving options data: {e}")
        return None

def get_futures_data(ticker, year, month, day):
    """
    Retrieve futures data from pickle files based on the ticker, year, month, and day.

    Parameters:
    - ticker (str): Ticker symbol ('BANKNIFTY' or 'NIFTY').
    - year (int): Year of the data.
    - month (int): Month of the data.
    - day (int): Day of the data.

    Returns:
    - data (pd.DataFrame or None): DataFrame containing futures data if successful, None if unsuccessful.
    """
    try:
        if ticker == 'BANKNIFTY':
            data = pd.read_pickle(r"D:\Banknifty Futures\{}\{}\{}_{}_{}.pkl".format(ticker, year, day, month, year))
            if not data.empty:
                return data
            
        elif ticker == 'NIFTY':
            data = pd.read_pickle(r"D:\Banknifty Futures\{}\{}\{}_{}_{}.pkl".format(ticker, year, day, month, year))
            if not data.empty:
                return data
            
    except Exception as e:
        print(f"Error occurred while retrieving futures data: {e}")
        return None
