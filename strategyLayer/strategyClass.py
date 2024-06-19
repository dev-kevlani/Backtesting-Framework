from strategyLayer.createLegs import create_leg

class BaseStrategy:
    def get_legs(self, timestamp, atm_strike):
        raise NotImplementedError("This method should be overridden by subclasses")

class LongCallStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy = atm_strike

        options_data = options_data[
            (options_data['strike_price'] == call_strike_buy)
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE')
        ], options_data

class ShortCallStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_sell = atm_strike

        options_data = options_data[
            (options_data['strike_price'] == call_strike_sell)
        ]

        return [
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE')
        ], options_data

class LongPutStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        put_strike_buy = atm_strike

        options_data = options_data[
            (options_data['strike_price'] == put_strike_buy)
        ]

        return [
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE')
        ], options_data

class ShortPutStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        put_strike_sell = atm_strike

        options_data = options_data[
            (options_data['strike_price'] == put_strike_sell)
        ]

        return [
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE')
        ], options_data

class bullCallSpreadStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy = atm_strike
        call_strike_sell = atm_strike + 100
        
        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy, call_strike_sell]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE')
        ]

class bullPutSpreadStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        put_strike_buy = atm_strike
        put_strike_sell = atm_strike - 100

        options_data = options_data[
            (options_data['strike_price'].isin([put_strike_buy, put_strike_sell]))
        ]
        
        return [
            create_leg(timestamp, put_strike_buy, 'buy', 'PE'),
            create_leg(timestamp, put_strike_sell, 'sell', 'PE')
        ]

class ironCondorStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_sell = atm_strike + 100
        call_strike_buy = atm_strike + 200
        put_strike_sell = atm_strike - 100
        put_strike_buy = atm_strike - 200

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy, call_strike_sell, put_strike_buy, put_strike_sell]))
        ]
        
        return [
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE'),
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE')
        ], options_data

class atmStraddleSell(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_sell = atm_strike
        put_strike_sell = atm_strike

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_sell, put_strike_sell]))
        ]
        
        return [
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE')
        ], options_data

class longStraddleStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy = atm_strike
        put_strike_buy = atm_strike

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy, put_strike_buy]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE')
        ], options_data

class longStrangleStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy = atm_strike + 100
        put_strike_buy = atm_strike - 100

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy, put_strike_buy]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE')
        ], options_data

class shortStrangleStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_sell = atm_strike + 100
        put_strike_sell = atm_strike - 100

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_sell, put_strike_sell]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE')
        ], options_data

class bearCallSpreadStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_sell = atm_strike
        call_strike_buy = atm_strike + 100

        return [
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE')
        ]

class bearPutSpreadStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        put_strike_sell = atm_strike
        put_strike_buy = atm_strike - 100

        return [
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE'),
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE')
        ]

class bearCallSpreadStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_sell = atm_strike
        call_strike_buy = atm_strike + 100

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_sell, call_strike_buy]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE')
        ], options_data

class shortIronButterflyStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_sell = atm_strike
        put_strike_sell = atm_strike
        call_strike_buy = atm_strike + 100
        put_strike_buy = atm_strike - 100

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_sell, put_strike_sell, call_strike_buy, put_strike_buy]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE'),
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE')
        ], options_data

class longIronButterflyStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy = atm_strike
        put_strike_buy = atm_strike
        call_strike_sell = atm_strike + 100
        put_strike_sell = atm_strike - 100

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy, put_strike_buy, call_strike_sell, put_strike_sell]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE'),
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE')
        ], options_data

class ratioCallSpreadStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy = atm_strike
        call_strike_sell = atm_strike + 100

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy, call_strike_sell]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE')
        ], options_data

class ratioPutSpreadStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        put_strike_buy = atm_strike
        put_strike_sell = atm_strike - 100

        options_data = options_data[
            (options_data['strike_price'].isin([put_strike_buy, put_strike_sell]))
        ]

        return [
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE'),
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE'),
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE')
        ], options_data

class butterflyCallSpreadStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy_low = atm_strike - 100
        call_strike_sell = atm_strike
        call_strike_buy_high = atm_strike + 100

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy_low, call_strike_sell, call_strike_buy_high]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy_low, 'buy', 'CE'),
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, call_strike_sell, 'sell', 'CE'),
            create_leg(options_data, timestamp, call_strike_buy_high, 'buy', 'CE')
        ], options_data

class butterflyPutSpreadStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        put_strike_buy_low = atm_strike - 100
        put_strike_sell = atm_strike
        put_strike_buy_high = atm_strike + 100

        options_data = options_data[
            (options_data['strike_price'].isin([put_strike_buy_low, put_strike_sell, put_strike_buy_high]))
        ]

        return [
            create_leg(options_data, timestamp, put_strike_buy_low, 'buy', 'PE'),
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE'),
            create_leg(options_data, timestamp, put_strike_sell, 'sell', 'PE'),
            create_leg(options_data, timestamp, put_strike_buy_high, 'buy', 'PE')
        ], options_data

class reverseIronCondorStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy_low = atm_strike - 200
        call_strike_sell_mid_low = atm_strike - 100
        call_strike_sell_mid_high = atm_strike + 100
        call_strike_buy_high = atm_strike + 200

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy_low, call_strike_sell_mid_low, call_strike_sell_mid_high, call_strike_buy_high]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy_low, 'buy', 'CE'),
            create_leg(options_data, timestamp, call_strike_sell_mid_low, 'sell', 'CE'),
            create_leg(options_data, timestamp, call_strike_sell_mid_high, 'sell', 'CE'),
            create_leg(options_data, timestamp, call_strike_buy_high, 'buy', 'CE')
        ], options_data

class longPutLadderStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        put_strike_buy = atm_strike
        put_strike_sell_mid = atm_strike - 100
        put_strike_sell_low = atm_strike - 200

        options_data = options_data[
            (options_data['strike_price'].isin([put_strike_buy, put_strike_sell_mid, put_strike_sell_low]))
        ]

        return [
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE'),
            create_leg(options_data, timestamp, put_strike_sell_mid, 'sell', 'PE'),
            create_leg(options_data, timestamp, put_strike_sell_low, 'sell', 'PE')
        ], options_data

class longCallLadderStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy = atm_strike
        call_strike_sell_mid = atm_strike + 100
        call_strike_sell_high = atm_strike + 200

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy, call_strike_sell_mid, call_strike_sell_high]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, call_strike_sell_mid, 'sell', 'CE'),
            create_leg(options_data, timestamp, call_strike_sell_high, 'sell', 'CE')
        ], options_data

class stripStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy = atm_strike
        put_strike_buy = atm_strike

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy, put_strike_buy]))
        ]

        return [
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE'),
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE'),
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE')
        ], options_data

class strapStrategy(BaseStrategy):
    def get_legs(self, options_data, timestamp, atm_strike):
        call_strike_buy = atm_strike
        put_strike_buy = atm_strike

        options_data = options_data[
            (options_data['strike_price'].isin([call_strike_buy, put_strike_buy]))
        ]

        return [
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, call_strike_buy, 'buy', 'CE'),
            create_leg(options_data, timestamp, put_strike_buy, 'buy', 'PE')
        ], options_data
