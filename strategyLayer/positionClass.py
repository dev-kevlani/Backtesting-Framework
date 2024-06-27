import pandas as pd
from datetime import timedelta
from utils.utils import *

class Position:
    def __init__(self, entry_timestamp, legs, stop_loss, target_profit, entry_premium, margin_used, strategy_type):
        """
        Initialize a position object with entry details.

        Parameters:
        - entry_timestamp (datetime): Timestamp when the position was entered.
        - legs (list): List of legs (options) comprising the position.
        - stop_loss (float): Stop loss value for the position.
        - target_profit (float): Target profit value for the position.
        - entry_premium (float): Premium paid or received upon entry.
        - margin_used (float): Margin utilized for the position.
        - strategy_type (str): Type of strategy ('credit' or 'debit').

        Attributes:
        - exit_premium (float or None): Premium received or paid upon exit.
        - exit_timestamp (datetime or None): Timestamp when the position was exited.
        - pnl (float or None): Profit or loss upon exit.
        """
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
        """
        Record exit details for the position.

        Parameters:
        - exit_timestamp (datetime): Timestamp when the position was exited.
        - pnl (float): Profit or loss upon exit.
        """
        self.exit_timestamp = exit_timestamp
        self.pnl = pnl

    def get_current_leg_prices(self, options_data, timestamp):
        """
        Retrieve current prices and Greeks for all legs of the position at a given timestamp.

        Parameters:
        - options_data (pd.DataFrame): DataFrame containing options data.
        - timestamp (datetime): Timestamp to fetch current prices.

        Returns:
        - max_exit_timestamp (datetime): Maximum timestamp encountered while fetching prices.
        - close_position (bool): Flag indicating if the position should be closed due to inability to fetch prices.
        """
        max_exit_timestamp = timestamp
        close_position = False
        timestamp_list = []

        for leg in self.legs:
            del_multiplier = get_delta_multiplier(leg['action'], leg['option_type'])
            all_greeks_multiplier = get_all_other_greeks_multiplier(leg['action'])

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

                    if isinstance(option, pd.Series):
                        current_leg = option if (option['strike_price'] == leg['strike_price'] and option['option_type'] == leg['option_type']) else None
                    else:
                        current_leg = option[(option['strike_price'] == leg['strike_price']) & (option['option_type'] == leg['option_type'])]

                    if current_leg is None or current_leg.empty:
                        timestamp += pd.Timedelta(seconds=1)
                        retries += 1
                    else:
                        if isinstance(current_leg, pd.Series):
                            current_price = current_leg['option_price'] * all_greeks_multiplier
                            leg['exit_delta'] = current_leg['delta'] * del_multiplier
                            leg['exit_theta'] = current_leg['theta'] * all_greeks_multiplier
                            leg['exit_gamma'] = current_leg['gamma'] * all_greeks_multiplier
                            leg['exit_iv'] = current_leg['iv'] * all_greeks_multiplier
                        else:
                            current_price = current_leg['option_price'].iloc[0] * all_greeks_multiplier
                            leg['exit_delta'] = current_leg['delta'].iloc[0] * del_multiplier
                            leg['exit_theta'] = current_leg['theta'].iloc[0] * all_greeks_multiplier
                            leg['exit_gamma'] = current_leg['gamma'].iloc[0] * all_greeks_multiplier
                            leg['exit_iv'] = current_leg['iv'] * all_greeks_multiplier

                        leg['exit_price'] = current_price
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

        return max_exit_timestamp, close_position
