import pandas as pd

def get_option_data(ticker, year, month, day):
    try:
        if ticker == 'BANKNIFTY':
            data = pd.read_pickle(r"D:\BNFDATA\options_data_backtest\pickles\{}_{}_{}.pkl".format(day, month, year))
            if (data.empty == False):
                return data
            
        elif ticker == 'NIFTY':
            data = pd.read_pickle(r"D:\NIFTYDATA\options_data\pickles\{}_{}_{}.pkl".format(day, month, year))
            if (data.empty == False):
                return data
    except Exception as e:
        return None
        
def get_futures_data(ticker, year, month, day):
    try:
        
        if ticker == 'BANKNIFTY':
            data = pd.read_pickle(r"D:\Banknifty Futures\{}\{}\{}_{}_{}.pkl".format(ticker, year, day, month, year))
            if (data.empty == False):
                return data
            
        elif ticker == 'NIFTY':
            data = pd.read_pickle(r"D:\Banknifty Futures\{}\{}\{}_{}_{}.pkl".format(ticker, year, day, month, year))
            if (data.empty == False):
                return data
            
    except Exception as e:
        return None