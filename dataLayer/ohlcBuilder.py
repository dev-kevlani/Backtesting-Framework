import pandas as pd

def create_ohlc_candles(tick_data, timeframe):
    """
    Aggregates tick data into OHLC candles based on the given timeframe.

    Parameters:
    - tick_data: A DataFrame containing tick data with columns ['timestamp', 'price', 'volume']
    - timeframe: A string representing the candle timeframe, e.g., '1T' for 1 minute, '5T' for 5 minutes

    Returns:
    - ohlc_data: A DataFrame containing OHLC candles
    """
    
    ohlc_data = tick_data['Close'].resample(timeframe).ohlc()
    
    if 'Volume' in tick_data.columns:
        ohlc_data['volume'] = tick_data['Volume'].resample(timeframe).sum()
    
    if 'OI' in tick_data.columns:
        ohlc_data['oi'] = tick_data['OI'].resample(timeframe).sum()
    
    return ohlc_data