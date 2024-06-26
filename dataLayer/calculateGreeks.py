from py_vollib_vectorized import vectorized_implied_volatility, vectorized_delta, vectorized_gamma, vectorized_rho, vectorized_theta
import pandas as pd
import numpy as np

def calculate_iv_and_greeks(options_data):
    """
    Calculate implied volatility (IV) and Greeks (delta, gamma, rho, theta) for options data.

    Parameters:
    - options_data (pd.DataFrame): DataFrame containing options data with columns:
        ['option_price', 'spot_price', 'strike_price', 'expiry_date', 'option_type']

    Returns:
    - options_data (pd.DataFrame): DataFrame with added columns:
        ['iv', 'delta', 'gamma', 'rho', 'theta'] containing calculated values
    """
    if options_data is None or options_data.empty:
        return None, None
    
    try:
        # Calculate time to expiry in days
        options_data['time_diff'] = pd.to_datetime(options_data['expiry_date']) - pd.to_datetime(options_data.index)
        options_data['time_to_expiry_days'] = options_data['time_diff'].dt.total_seconds() / (24 * 3600) / 365
        options_data.drop(columns=['time_diff'], inplace=True)
        
        # Set risk-free rate
        options_data['r'] = 0.0625

        # Extract necessary data for calculations
        option_prices = options_data['option_price'].values
        spot_prices = options_data['spot_price'].values
        strike_prices = options_data['strike_price'].values
        times_to_expiry = options_data['time_to_expiry_days'].values
        risk_free_rates = options_data['r'].values
        option_types = options_data['option_type'].fillna('').apply(lambda x: 'c' if x == 'CE' else 'p').values
        
    except KeyError as e:
        # Handle missing keys by assigning NaNs to IV and Greeks arrays
        iv = np.full(len(options_data), np.nan)
        delta = np.full(len(options_data), np.nan)
        gamma = np.full(len(options_data), np.nan)
        rho = np.full(len(options_data), np.nan)
        theta = np.full(len(options_data), np.nan)

    try:
        # Calculate IV and Greeks using vectorized functions
        iv = vectorized_implied_volatility(
            option_prices, spot_prices, strike_prices, times_to_expiry, risk_free_rates, option_types,
            q=0, on_error='warn', model='black_scholes_merton', return_as='numpy'
        )
        delta = vectorized_delta(
            option_types, spot_prices, strike_prices, times_to_expiry, risk_free_rates, iv,
            q=0, model='black_scholes', return_as='numpy'
        )
        gamma = vectorized_gamma(
            option_types, spot_prices, strike_prices, times_to_expiry, risk_free_rates, iv,
            q=0, model='black_scholes', return_as='numpy'
        )
        rho = vectorized_rho(
            option_types, spot_prices, strike_prices, times_to_expiry, risk_free_rates, iv,
            q=0, model='black_scholes', return_as='numpy'
        )
        theta = vectorized_theta(
            option_types, spot_prices, strike_prices, times_to_expiry, risk_free_rates, iv,
            q=0, model='black_scholes', return_as='numpy'
        )
        
    except ZeroDivisionError as e:
        # Handle ZeroDivisionError by assigning NaNs to IV and Greeks arrays
        print(f"ZeroDivisionError occurred: {e}")
        iv = np.full(len(options_data), np.nan)
        delta = np.full(len(options_data), np.nan)
        gamma = np.full(len(options_data), np.nan)
        rho = np.full(len(options_data), np.nan)
        theta = np.full(len(options_data), np.nan)
    
    # Assign calculated values back to options_data DataFrame
    options_data['iv'] = iv
    options_data['delta'] = delta
    options_data['gamma'] = gamma
    options_data['rho'] = rho
    options_data['theta'] = theta

    return options_data
