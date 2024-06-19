import pandas as pd
from strategyLayer.createLegs import create_leg

class DynamicLegStrategy:
    def __init__(self):
        print("calling Strategy class")

    def get_legs(self, options_data, timestamp, atm_strike, instruments_with_actions):
        legs = []
        strikes_and_types = []

        for instrument in instruments_with_actions:
            strike_price, option_type, action, lots = atm_strike + instrument['strike_part'], instrument['option_type'], instrument['action'], instrument['lots']
            strikes_and_types.append((strike_price, option_type))
            
            options_data_filtered = options_data[
                (options_data['strike_price'] == strike_price) &
                (options_data['option_type'] == option_type)
            ]
            
            leg = create_leg(options_data_filtered, timestamp, strike_price, action, option_type, lots)
            legs.append(leg)
        
        strikes_and_types_df = pd.DataFrame(strikes_and_types, columns=['strike_price', 'option_type'])
        options_data['Timestamp'] = options_data.index
        filtered_options_data = options_data.merge(strikes_and_types_df, on=['strike_price', 'option_type'])
        filtered_options_data.set_index('Timestamp', inplace=True)
        
        return legs, filtered_options_data