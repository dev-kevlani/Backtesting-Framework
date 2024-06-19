import pandas as pd
from datetime import time
from strategyLayer.positionClass import *
from strategyLayer.createLegs import *
from strategyLayer.strategyClass import *
from strategyLayer.dynamicInstruments import *
class SpreadBacktester:
    def __init__(self, options_data, signals, stop_loss, target_profit, instruments_with_actions, sl_percentage_based, tp_percentage_based):
        self.options_data = options_data
        self.signals = signals
        self.stop_loss = stop_loss
        self.target_profit = target_profit
        self.instruments_with_actions = instruments_with_actions
        self.sl_percentage_based = sl_percentage_based
        self.tp_percentage_based = tp_percentage_based
        self.positions = []
        self.trades = []
        self.portfolio_metrics = {'delta': 0, 'theta': 0, 'gamma': 0}

    def generate_signals(self):
        self.signals['entry_signal'] = self.signals['final_signal'].apply(lambda x: True if x == 1 else False)
        self.signals['exit_signal'] = self.signals['final_signal'].apply(lambda x: True if x == -1 else False)
        self.options_data = self.options_data.join(self.signals[['entry_signal', 'exit_signal']], how='left')
        
    def check_entry_signal(self, timestamp):
        next_timestamp = self.options_data[self.options_data['entry_signal'] & (self.options_data.index > timestamp)].index.min()
        return next_timestamp

    def execute_trades(self):
        timestamp = self.options_data.index[0]
        while timestamp.time() <= time(15, 0):
            timestamp = self.check_entry_signal(timestamp)
            if timestamp:
                bool_var = self.enter_spread(timestamp)
                if bool_var == False:
                    timestamp = timestamp + timedelta(seconds=1)
                    continue
                timestamp = self.manage_positions(timestamp + timedelta(seconds=1))
            else:
                break
        return self.trades

    def enter_spread(self, timestamp):
        try:
            min_diff = self.options_data.loc[timestamp]['Difference'].min()
            atm_strike = self.options_data.loc[timestamp][self.options_data.loc[timestamp]['Difference'] == min_diff]['strike_price'].iloc[0]
            strategy = DynamicLegStrategy()
            legs, self.filtered_options_data = strategy.get_legs(self.options_data, timestamp, atm_strike, self.instruments_with_actions)
            premium = sum((leg['entry_price'] * leg['lot_size']) for leg in legs)
            margin_used = sum(leg['margin_used'] for leg in legs)
            strat_type = 'credit' if premium < 0 else 'debit'
            
            if self.sl_percentage_based:
                stop_loss = (abs(premium) * self.stop_loss) if premium < 0 else (abs(premium) * (1 - (self.stop_loss - 1)))
            else:
                stop_loss = (abs(premium) + self.stop_loss) if premium < 0 else (abs(premium) - self.stop_loss)
            
            if self.tp_percentage_based:
                target_profit = abs(premium) * self.target_profit if premium < 0 else (abs(premium) * (1 + (1 - self.target_profit)))
            else:
                target_profit = (abs(premium) - self.target_profit) if premium < 0 else (abs(premium) + self.target_profit)
            
            position = Position(
                entry_timestamp=timestamp,
                legs=legs,
                premium=premium,
                strategy_type=strat_type,
                margin_used=margin_used,
                stop_loss=stop_loss,
                target_profit=target_profit
            )
            self.positions.append(position)
            return True
        except KeyError as e:
            return False

    def manage_positions(self, timestamp):
        if self.positions:
            position = self.positions[0]
            if position.exit_timestamp is None:
                exit_timestamp = self.check_exit_conditions(position, timestamp)
                return exit_timestamp 
        return timestamp

    def check_exit_conditions(self, position, timestamp):
        max_exit_timestamp = timestamp
        while max_exit_timestamp.time() <= time(15, 15):
            current_prices, max_exit_timestamp, close_position = position.get_current_leg_prices(self.filtered_options_data, max_exit_timestamp)
            if close_position:
                self.positions.remove(position)
                return max_exit_timestamp

            total_price = sum(current_prices)
            
            if position.strategy_type == 'credit':
                if self.sl_percentage_based:
                    stop_loss = position.stop_loss
                    target_profit = position.target_profit
                else:
                    stop_loss = (abs(total_price) >= position.stop_loss)
                    target_profit = (abs(total_price) <= position.target_profit)
            else:
                if self.sl_percentage_based:
                    stop_loss = position.stop_loss
                    target_profit = position.target_profit
                else:
                    stop_loss = (abs(total_price) <= position.stop_loss)
                    target_profit = (abs(total_price) >= position.target_profit)

            if stop_loss or target_profit:
                self.close_position(position, max_exit_timestamp, current_prices)
                return max_exit_timestamp

            max_exit_timestamp += pd.Timedelta(seconds=1)
        self.close_position(position, max_exit_timestamp, current_prices)
        return max_exit_timestamp

    def close_position(self, position, timestamp, current_prices):
        pnl = (sum(current_price - leg['entry_price'] for leg, current_price in zip(position.legs, current_prices)))*15
        position.add_exit_details(timestamp, pnl)
        self.trades.append({
            'entry_timestamp': position.entry_timestamp,
            'exit_timestamp': position.exit_timestamp,
            'pnl': position.pnl,
            'legs': position.legs
        })
        self.positions.remove(position)
