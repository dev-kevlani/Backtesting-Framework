import pandas as pd
from datetime import time
from strategyLayer.positionClass import *
from strategyLayer.createLegs import *
from strategyLayer.strategyClass import *
from strategyLayer.dynamicInstruments import *

class SpreadBacktester:
    def __init__(self, options_data, signals, stop_loss, target_profit, instruments_with_actions, sl_percentage_based, tp_percentage_based, strategy_type):
        """
        Initialize the SpreadBacktester with necessary parameters.

        Args:
        - options_data (DataFrame): Options data containing relevant information.
        - signals (DataFrame): DataFrame containing trading signals.
        - stop_loss (float): Stop loss value for exiting positions.
        - target_profit (float): Target profit value for exiting positions.
        - instruments_with_actions (dict): Dictionary defining actions for different strategies.
        - sl_percentage_based (bool): Whether stop loss is percentage-based.
        - tp_percentage_based (bool): Whether target profit is percentage-based.
        - strategy_type (str): Type of strategy ('directional' or other).
        """
        self.options_data = options_data
        self.signals = signals
        
        # Ensure all signal columns are initialized as False where NaN exists
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
        self.portfolio_metrics = {
                                'current_timestamp': None,
                                'net_port_pnl': 0,
                                'port_delta': 0,
                                'port_theta': 0,
                                'port_gamma': 0,
                                'port_iv': 0
                            }

    def classifying_signals(self):
        """
        Classify trading signals into new entry and exit signals based on strategy type.

        Returns:
        - Timestamp: Timestamp of the first signal to process.
        """
        if self.strategy_type == 'directional':
            self.signals['new_entry_signal'] = self.signals.apply(lambda x: 'long' if x['long_signal_entry'] else 'short' if x['short_signal_entry'] else 'nothing', axis=1)
            self.signals['new_exit_signal'] = self.signals.apply(lambda x: 'long' if x['long_signal_exit'] else 'short' if x['short_signal_exit'] else 'nothing', axis=1)
        else:
            self.signals['new_entry_signal'] = self.signals.apply(lambda x: True if (x['long_signal_entry'] or x['short_signal_entry'] or x['entry_signal']) else False, axis=1)
            self.signals['new_exit_signal'] = self.signals.apply(lambda x: True if (x['long_signal_exit'] or x['short_signal_exit'] or x['exit_signal']) else False, axis=1)
        
        return self.signals.index[0]

    def execute_trades(self, timestamp):
        """
        Execute trades based on generated signals.

        Args:
        - timestamp (Timestamp): Starting timestamp for executing trades.

        Returns:
        - Tuple: List of executed trades and count of uncounted positions.
        """
        while True:
            signals_subset = self.signals[['new_entry_signal', 'new_exit_signal']][timestamp:]
            if signals_subset.empty:
                break
            
            for idx, (index, row) in enumerate(signals_subset.iterrows()):
                if index.time() >= time(15, 15):
                    return self.trades, self.positions_not_counted
                
                if row['new_entry_signal'] == 'long' or row['new_entry_signal'] == 'short':
                    bool_var, upd_timestamp = self.enter_spread(index)
                    
                    if not bool_var:
                        timestamp = upd_timestamp + timedelta(seconds=1)
                        break
                    
                    timestamp = self.manage_positions(upd_timestamp + timedelta(seconds=1))
                    break
            else:
                break
        
        return self.trades, self.positions_not_counted

    def enter_spread(self, timestamp):
        """
        Enter into a spread position based on the current trading signals.

        Args:
        - timestamp (Timestamp): Timestamp for entering the spread position.

        Returns:
        - Tuple: Boolean indicating success of entry, updated timestamp.
        """
        try:
            entry_signal = self.signals.loc[timestamp, 'new_entry_signal']
            
            # Determine instruments based on strategy type
            if self.strategy_type == 'directional':
                if entry_signal in self.instruments_with_actions['directional']:
                    instruments = self.instruments_with_actions['directional'][entry_signal]
                else:
                    return False, timestamp
            else:
                instruments = self.instruments_with_actions[self.strategy_type]
            
            # Find ATM strike price
            min_diff = self.options_data.loc[timestamp]['Difference'].min()
            atm_strike = self.options_data.loc[timestamp][self.options_data.loc[timestamp]['Difference'] == min_diff]['strike_price'].iloc[0]
            
            # Generate legs for the spread strategy
            strategy = DynamicLegStrategy()
            legs, self.filtered_options_data = strategy.get_legs(self.options_data, timestamp, atm_strike, instruments)
            
            # Calculate entry premium and margin used
            entry_premium = sum((leg['entry_price'] * leg['lot_size']) for leg in legs)
            margin_used = sum(leg['margin_used'] for leg in legs)
            strat_type = 'credit' if entry_premium < 0 else 'debit'
            
            # Calculate stop loss and target profit
            if self.sl_percentage_based:
                stop_loss = (abs(entry_premium) * self.stop_loss) if entry_premium < 0 else (abs(entry_premium) * (1 - (self.stop_loss - 1)))
            else:
                stop_loss = (abs(entry_premium) + self.stop_loss) if entry_premium < 0 else (abs(entry_premium) - self.stop_loss)
            
            if self.tp_percentage_based:
                target_profit = abs(entry_premium) * self.target_profit if entry_premium < 0 else (abs(entry_premium) * (1 + (1 - self.target_profit)))
            else:
                target_profit = (abs(entry_premium) - self.target_profit) if entry_premium < 0 else (abs(entry_premium) + self.target_profit)
            
            # Create a new position and add it to the positions list
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
            return True, timestamp
        
        except KeyError as e:
            return False, timestamp

    def manage_positions(self, timestamp):
        """
        Manage open positions by checking exit conditions.

        Args:
        - timestamp (Timestamp): Timestamp for managing positions.

        Returns:
        - Timestamp: Updated timestamp after managing positions.
        """
        if self.positions:
            position = self.positions[0]
            if position.exit_timestamp is None:
                exit_timestamp = self.check_exit_conditions(position, timestamp)
                return exit_timestamp 
        return timestamp

    def check_exit_conditions(self, position, timestamp):
        """
        Check exit conditions for a given position.

        Args:
        - position (Position): Position object to check exit conditions for.
        - timestamp (Timestamp): Timestamp for checking exit conditions.

        Returns:
        - Timestamp: Timestamp of exit or maximum exit timestamp.
        """
        max_exit_timestamp = timestamp
        while max_exit_timestamp.time() <= time(15, 15):
            max_exit_timestamp, close_position = position.get_current_leg_prices(self.filtered_options_data, max_exit_timestamp)
            if close_position:
                self.positions_not_counted += 1
                self.positions.remove(position)
                return max_exit_timestamp
            
            exit_premium = sum((leg['exit_price'] * leg['lot_size']) for leg in position.legs)
            position.exit_premium = exit_premium
            
            # Check exit conditions based on strategy type
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
        
        # Close position due to time breach
        self.close_position(position, max_exit_timestamp, 'time_breach')
        return max_exit_timestamp

    def close_position(self, position, timestamp, reason):
        """
        Close a position and record the trade details.

        Args:
        - position (Position): Position object to close.
        - timestamp (Timestamp): Timestamp of position closure.
        - reason (str): Reason for closing the position.
        """
        pnl = position.exit_premium - position.entry_premium
        transaction_cost = sum((abs(leg['entry_price'] + leg['exit_price']) * leg['lot_size']) * 0.001 for leg in position.legs)
        
        # Add exit details to the position and record
                # Add exit details to the position and record the trade
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
        
        # Remove the position from the positions list
        self.positions.remove(position)


    def update_portfolio_metrics(self, timestamp, position):
        """
        Manage portfolio Greeks and implement hedging strategies or position adjustments.

        Parameters:
        - timestamp (Timestamp): Current timestamp for managing portfolio.
        """
        transaction_cost = 0
        pnl = position.exit_premium - position.entry_premium
        

        for leg in position.legs:
            self.portfolio_metrics['port_delta'] += leg['delta'] * leg['lot_size']
            self.portfolio_metrics['port_gamma'] += leg['gamma'] * leg['lot_size']
            self.portfolio_metrics['port_theta'] += leg['theta'] * leg['lot_size']
            self.portfolio_metrics['port_iv'] += leg['iv'] * leg['lot_size']
            transaction_cost += (abs(leg['entry_price'] + leg['exit_price']) * leg['lot_size']) * 0.001
        
        self.portfolio_metrics['current_timestamp'] = timestamp
        self.portfolio_metrics['net_port_pnl'] += (pnl-transaction_cost)

        