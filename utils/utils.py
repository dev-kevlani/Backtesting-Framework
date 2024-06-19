def get_multiplier(action, option_type):
        return 1 if ((action == 'buy' and option_type == 'CE') or (action == 'sell' and option_type == 'PE')) else -1