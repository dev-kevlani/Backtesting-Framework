import pandas as pd
from strategyLayer.createLegs import create_leg

class DynamicLegStrategy:
    def __init__(self):
        """
        Initialize the DynamicLegStrategy class.
        """
        print("calling Strategy class")

    def get_legs(self, options_data, timestamp, atm_strike, instruments_with_actions):
        """
        Generate legs (options) based on given criteria.

        Parameters:
        - options_data (pd.DataFrame): DataFrame containing options data.
        - timestamp (datetime): Timestamp for selecting options data.
        - atm_strike (float): ATM (at-the-money) strike price.
        - instruments_with_actions (list): List of dictionaries specifying strike part, option type, action, and lots.

        Returns:
        - legs (list): List of created legs (options).
        - filtered_options_data (pd.DataFrame): Filtered options data based on selected strikes and types.
        """
        legs = []
        strikes_and_types = []

        for instrument in instruments_with_actions:
            strike_price = atm_strike + instrument['strike_part']
            option_type = instrument['option_type']
            action = instrument['action']
            lots = instrument['lots']
            
            # Filter options data based on strike price and option type
            options_data_filtered = options_data[
                (options_data['strike_price'] == strike_price) &
                (options_data['option_type'] == option_type)
            ]
            
            # Create a leg (option) using filtered options data
            leg = create_leg(options_data_filtered, timestamp, strike_price, action, option_type, lots)
            legs.append(leg)
            strikes_and_types.append((strike_price, option_type))
        
        # Create DataFrame with selected strikes and types for further processing
        strikes_and_types_df = pd.DataFrame(strikes_and_types, columns=['strike_price', 'option_type'])
        
        # Merge strikes and types with options data to get filtered options data
        options_data['Timestamp'] = options_data.index
        filtered_options_data = options_data.merge(strikes_and_types_df, on=['strike_price', 'option_type'])
        filtered_options_data.set_index('Timestamp', inplace=True)
        filtered_options_data = filtered_options_data.loc[timestamp:]
        
        return legs, filtered_options_data
