import pandas as pd
from datetime import time
from strategyLayer.positionClass import *
from strategyLayer.createLegs import *
from strategyLayer.strategyClass import *
from strategyLayer.dynamicInstruments import *

class SpreadBacktester:
    def __init__(self, options_data, signals, stop_loss, target_profit, instruments_with_actions, sl_percentage_based, tp_percentage_based, strategy_type):
        self.options_data = options_data
        self.signals = signals
        for col in self.signals.filter(like='signal').columns:
            if self.signals.filter(like='signal')[col].isnull().any():
                self.signals[col] = False
        self.stop_loss = stop_loss
        self.target_profit = target_profit
        self.instruments_with_actions = instruments_with_actions
        self.sl_percentage_based = sl_percentage_based
        self.tp_percentage_based = tp_percentage_based
        self.strategy_type = strategy_type
        self.positions = []
        self.trades = []
        self.positions_not_counted = 0
        self.portfolio_metrics = {'delta': 0, 'theta': 0, 'gamma': 0}

    def classifying_signals(self):
        if self.strategy_type == 'directional':
            self.signals['new_entry_signal'] = self.signals.apply(lambda x: 'long' if x['long_signal_entry'] else 'short' if x['short_signal_entry'] else 'nothing', axis=1)
            self.signals['new_exit_signal'] = self.signals.apply(lambda x: 'long' if x['long_signal_exit'] else 'short' if x['short_signal_exit'] else 'nothing', axis=1)
        else:
            self.signals['new_entry_signal'] = self.signals.apply(lambda x: True if (x['long_signal_entry'] or x['short_signal_entry'] or x['entry_signal']) else False, axis=1)
            self.signals['new_exit_signal'] = self.signals.apply(lambda x: True if (x['long_signal_exit'] or x['short_signal_exit'] or x['exit_signal']) else False, axis=1)
        
        return self.signals.index[0]

    def execute_trades(self, timestamp):
        for idx, (index, row) in enumerate(self.signals[['new_entry_signal', 'new_exit_signal']][timestamp:].iterrows()):
            if row['new_entry_signal'] == 'long' or row['new_entry_signal'] == 'short' :
                bool_var = self.enter_spread(timestamp)
                if bool_var == False:
                    timestamp = timestamp + timedelta(seconds=1)
                    continue
                timestamp = self.manage_positions(timestamp + timedelta(seconds=1))
                self.execute_trades(timestamp)
                
            elif timestamp.time() < time(15,15):
                continue
            else:
                break
        return self.trades, self.positions_not_counted

    def enter_spread(self, timestamp):
        try:
            entry_signal = self.signals.loc[timestamp, 'new_entry_signal']
            if self.strategy_type == 'directional':
                if entry_signal in self.instruments_with_actions['directional']:
                    instruments = self.instruments_with_actions['directional'][entry_signal]
                else:
                    return False
            else:
                instruments = self.instruments_with_actions[self.strategy_type]
            
            min_diff = self.options_data.loc[timestamp]['Difference'].min()
            atm_strike = self.options_data.loc[timestamp][self.options_data.loc[timestamp]['Difference'] == min_diff]['strike_price'].iloc[0]
            
            strategy = DynamicLegStrategy()
            legs, self.filtered_options_data = strategy.get_legs(self.options_data, timestamp, atm_strike, instruments)
            
            entry_premium = sum((leg['entry_price'] * leg['lot_size']) for leg in legs)
            margin_used = sum(leg['margin_used'] for leg in legs)
            strat_type = 'credit' if entry_premium < 0 else 'debit'
            
            if self.sl_percentage_based:
                stop_loss = (abs(entry_premium) * self.stop_loss) if entry_premium < 0 else (abs(entry_premium) * (1 - (self.stop_loss - 1)))
            else:
                stop_loss = (abs(entry_premium) + self.stop_loss) if entry_premium < 0 else (abs(entry_premium) - self.stop_loss)
            
            if self.tp_percentage_based:
                target_profit = abs(entry_premium) * self.target_profit if entry_premium < 0 else (abs(entry_premium) * (1 + (1 - self.target_profit)))
            else:
                target_profit = (abs(entry_premium) - self.target_profit) if entry_premium < 0 else (abs(entry_premium) + self.target_profit)
            
            position = Position(
                entry_timestamp=timestamp,
                legs=legs,
                entry_premium=entry_premium,
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
            exit_premium = sum((leg['exit_price'] * leg['lot_size']) for leg in position.legs)
            position.exit_premium = exit_premium
            if close_position:
                self.positions_not_counted+=1
                self.positions.remove(position)
                return max_exit_timestamp

            if position.strategy_type == 'credit':
                
                if (abs(position.exit_premium) >= position.stop_loss):
                    self.close_position(position, max_exit_timestamp, 'SL_hit')
                    return max_exit_timestamp

                elif (abs(position.exit_premium) <= position.target_profit):
                    self.close_position(position, max_exit_timestamp, 'TP_hit')
                    return max_exit_timestamp
            
            elif position.strategy_type == 'debit':
                if (abs(position.exit_premium) <= position.stop_loss):
                    self.close_position(position, max_exit_timestamp, 'SL_hit')
                    return max_exit_timestamp

                elif (abs(position.exit_premium) >= position.target_profit):
                    self.close_position(position, max_exit_timestamp, 'TP_hit')
                    return max_exit_timestamp

            max_exit_timestamp += pd.Timedelta(seconds=1)
        self.close_position(position, max_exit_timestamp, 'time_breach')
        return max_exit_timestamp

    def close_position(self, position, timestamp, reason):
        pnl = position.exit_premium - position.entry_premium
        transaction_cost = sum((abs(leg['entry_price'] + leg['exit_price'])*leg['lot_size'])*0.001 for leg in position.legs)
        position.add_exit_details(timestamp, pnl)
        self.trades.append({
            'entry_timestamp': position.entry_timestamp,
            'exit_timestamp': position.exit_timestamp,
            'margin_used': position.margin_used,
            'entry_premium': position.entry_premium,
            'exit_premium': position.exit_premium,
            'strategy_type': position.strategy_type,
            'exit_reason': reason,
            'pnl': position.pnl,
            'transaction_cost': transaction_cost,
            'legs': position.legs
        })
        self.positions.remove(position)
