def get_delta_multiplier(action, option_type):
        return 1 if ((action == 'buy' and option_type == 'CE') or (action == 'sell' and option_type == 'PE')) else -1

def get_all_other_greeks_multiplier(action):
        return 1 if (action == 'buy') else -1