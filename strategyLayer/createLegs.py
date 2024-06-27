from datetime import timedelta
from utils.utils import *

def create_leg(options_data, timestamp, strike_price, action, option_type, lots):
    """
    Create a leg (option) based on given options data and parameters.

    Parameters:
    - options_data (pd.DataFrame): DataFrame containing options data.
    - timestamp (datetime): Timestamp for selecting options data.
    - strike_price (float): Strike price of the option.
    - action (str): Action type ('buy' or 'sell').
    - option_type (str): Option type ('call' or 'put').
    - lots (int): Number of lots (contracts).

    Returns:
    - leg_data (dict): Dictionary containing details of the created leg.
    """
    while True:
        try:
            # Attempt to locate option data at the specified timestamp
            option = options_data.loc[timestamp]
            if not option.empty:
                break
        except KeyError:
            pass
        # If data is not found at timestamp, increment timestamp by one second and retry
        timestamp = timestamp + timedelta(seconds=1)

    # Calculate margin based on action type
    margin = (-100000 * lots) if action == 'sell' else (option['option_price'] * 15 * lots)
    
    # Calculate multipliers for delta and all other Greeks
    del_multiplier = get_delta_multiplier(action, option_type)
    all_greeks_multiplier = get_all_other_greeks_multiplier(action)
    
    # Construct leg data dictionary with calculated values
    leg_data = {
        'entry_time_of_leg': timestamp,
        'strike_price': strike_price,
        'option_type': option_type,
        'action': action,
        'lot_size': lots,
        'margin_used': margin,
        'entry_price': option['option_price'] * all_greeks_multiplier,
        'entry_delta': option['delta'] * del_multiplier,
        'entry_theta': option['theta'] * all_greeks_multiplier,
        'entry_gamma': option['gamma'] * all_greeks_multiplier,
        'entry_iv': option['iv'] * all_greeks_multiplier,
        'exit_time_of_leg': None,
        'exit_price': None,
        'exit_delta': None,
        'exit_theta': None,
        'exit_gamma': None,
        'exit_iv': None
    }
    
    return leg_data
