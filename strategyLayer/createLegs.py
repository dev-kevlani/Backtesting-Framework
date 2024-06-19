from datetime import timedelta
from utils.utils import *

def create_leg(options_data, timestamp, strike_price, action, option_type, lots):
    while True:
        try:
            option = options_data.loc[timestamp]
            if not option.empty:
                break
        except KeyError:
            pass
        timestamp = timestamp + timedelta(seconds=1)

    margin = (-100000*lots) if action == 'sell' else (option['option_price'] * 15 * lots)
    multiplier = get_multiplier(action, option_type)
    
    leg_data = {
        'entry_time_of_leg': timestamp,
        'strike_price': strike_price,
        'option_type': option_type,
        'action': action,
        'lot_size': lots,
        'margin_used': margin,
        'entry_price': option['option_price'] if action == 'buy' else -option['option_price'],
        'entry_delta': option['delta'] * multiplier,
        'entry_theta': option['theta'] * multiplier,
        'entry_gamma': option['gamma'] * multiplier,
        'exit_time_of_leg': None,
        'exit_price': None,
        'exit_delta': None,
        'exit_theta': None,
        'exit_gamma': None
    }
    return leg_data
