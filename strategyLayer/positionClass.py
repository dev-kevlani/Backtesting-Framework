import pandas as pd
from datetime import datetime, timedelta, time
from utils.utils import *

class Position:
    def __init__(self, entry_timestamp, legs, stop_loss, target_profit, entry_premium, margin_used, strategy_type):
        self.entry_timestamp = entry_timestamp
        self.legs = legs
        self.entry_premium = entry_premium
        self.margin_used = margin_used
        self.strategy_type = strategy_type
        self.stop_loss = stop_loss
        self.target_profit = target_profit
        self.exit_premium = None
        self.exit_timestamp = None
        self.pnl = None

    def add_exit_details(self, exit_timestamp, pnl):
        self.exit_timestamp = exit_timestamp
        self.pnl = pnl

    def get_current_leg_prices(self, options_data, timestamp):
        current_prices = []
        max_exit_timestamp = timestamp
        close_position = False
        timestamp_list = []

        for leg in self.legs:
            multiplier = get_multiplier(leg['action'], leg['option_type'])
            current_price = None
            retries = 0
            max_retries = 10

            while current_price is None and retries < max_retries:
                if timestamp not in options_data.index:
                    timestamp += pd.Timedelta(seconds=1)
                    retries += 1
                    continue
                try:
                    option = options_data.loc[timestamp]
                    current_leg = option[(option['strike_price'] == leg['strike_price']) & (option['option_type'] == leg['option_type'])]
                    if current_leg.empty:
                        timestamp += pd.Timedelta(seconds=1)
                        retries += 1
                    else:
                        current_price = current_leg['option_price'].iloc[0] if leg['action'] == 'buy' else -current_leg['option_price'].iloc[0]
                        leg['exit_price'] = current_price
                        leg['exit_delta'] = current_leg['delta'].iloc[0] * multiplier
                        leg['exit_theta'] = current_leg['theta'].iloc[0] * multiplier
                        leg['exit_gamma'] = current_leg['gamma'].iloc[0] * multiplier
                        timestamp_list.append(timestamp)
                        if timestamp > max_exit_timestamp:
                            max_exit_timestamp = timestamp
                        leg['exit_time_of_leg'] = max_exit_timestamp
                except Exception as e:
                    timestamp += pd.Timedelta(seconds=1)
                    retries += 1
                    continue
            if current_price is None:
                close_position = True
                break

            current_prices.append(current_price)

        return current_prices, max_exit_timestamp, close_position