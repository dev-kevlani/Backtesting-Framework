import pandas as pd
import numpy as np

def all_indicators(args):
    
    def calculate_rsi(data, column, window):
        price_diff = data[column].diff()
        gain = price_diff.where(price_diff > 0, 0)
        loss = -price_diff.where(price_diff < 0, 0)
        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()
        rs = avg_gain / avg_loss
        data["{}_rsi".format(column)] = 100 - (100 / (1 + rs))

        return data
    
    def calculate_stoch(data, column, k_window, d_window):
        lowest_low = data[column].rolling(window=k_window).min()
        highest_high = data[column].rolling(window=k_window).max()
        data[f'{column}_k_percent'] = ((data[column] - lowest_low) / (highest_high - lowest_low)) * 100
        data[f'{column}_d_percent'] = data[f'{column}_k_percent'].rolling(window=d_window).mean()
        
        return data

    def calculate_sma(data, window):
        return data['close'].rolling(window=window).mean()

    def calculate_ema_without_adjust(data, window):
        return data['close'].ewm(span=window, adjust=False).mean()

    def calculate_ema_with_adjust(data, window):
        return data['close'].ewm(span=window, adjust=True).mean()

    def calculate_wma(data, window):
        weights = np.arange(1, window + 1)
        return data['close'].rolling(window=window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

    def calculate_hma(data, period):
        half_period = period // 2

        wma_half = data['close'].rolling(window=half_period).mean()
        wma_full = data['close'].rolling(window=period).mean()

        hull_moving_avg = pd.Series(2 * wma_half - wma_full).rolling(window=int(np.sqrt(period))).mean()
        hma = pd.Series(hull_moving_avg).rolling(window=int(np.sqrt(period))).mean()

        return hma

    def calculate_macd(data, short_window, long_window, signal_window):
        short_ema = data['close'].ewm(span=short_window, adjust=False).mean()
        long_ema = data['close'].ewm(span=long_window, adjust=False).mean()

        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()

        return macd_line, signal_line

    def calculate_stochastic_oscillator(data, k_window, d_window):
        lowest_low = data['low'].rolling(window=k_window).min()
        highest_high = data['high'].rolling(window=k_window).max()
        stoch_k_percent = ((data['close'] - lowest_low) / (highest_high - lowest_low)) * 100
        stoch_d_percent = stoch_k_percent.rolling(window=d_window).mean()
        return stoch_k_percent, stoch_d_percent

    def calculate_atr(data, window):
        tr = pd.DataFrame(index=data.index)
        tr['H-L'] = data['high'] - data['low']
        tr['H-PC'] = np.abs(data['high'] - data['close'].shift(1))
        tr['L-PC'] = np.abs(data['low'] - data['close'].shift(1))
        tr['TR'] = tr[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        return tr['TR'], tr['TR'].rolling(window=window).mean()

    def calculate_cci_on_sma(data, window):
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        sma = typical_price.rolling(window=window).mean()
        mad = lambda x: np.mean(np.abs(x - np.mean(x)))
        mean_deviation = typical_price.rolling(window=window).apply(mad, raw=True)
        cci_sma = (typical_price - sma) / (0.015 * mean_deviation)

        return cci_sma

    def calculate_cci_on_ema(data, window):
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        ema = typical_price.ewm(span=window, adjust=False).mean()
        mad = lambda x: np.mean(np.abs(x - np.mean(x)))
        mean_deviation = typical_price.rolling(window=window).apply(mad, raw=True)
        cci_ema = (typical_price - ema) / (0.015 * mean_deviation)

        return cci_ema

    def calculate_detrended_price_oscillator_on_sma(data, window):
        sma = data['close'].rolling(window=window).mean()
        dpo = data['close'] - sma.shift(int(window/2) + 1)
        return dpo

    def calculate_detrended_price_oscillator_on_ema(data, window):
        ema = data['close'].ewm(span=window, adjust=False).mean()
        dpo = data['close'] - ema.shift(int(window/2) + 1)
        return dpo

    def calculate_trix_on_sma(data, window):
        sma1 = data['close'].rolling(window=window).mean()
        sma2 = sma1.rolling(window=window).mean()
        sma3 = sma2.rolling(window=window).mean()
        trix = ((sma3 - sma3.shift(1)) / sma3.shift(1)) * 100
        return trix

    def calculate_trix_on_ema(data, window):
        ema1 = data['close'].ewm(span=window, adjust=False).mean()
        ema2 = ema1.ewm(span=window, adjust=False).mean()
        ema3 = ema2.ewm(span=window, adjust=False).mean()
        trix = ((ema3 - ema3.shift(1)) / ema3.shift(1)) * 100
        return trix

    def calculate_ichimoku_cloud(data, conversion_window, base_window):
        conversion_line = (data['high'].rolling(window=conversion_window).max() + data['low'].rolling(window=conversion_window).min()) / 2
        base_line = (data['high'].rolling(window=base_window).max() + data['low'].rolling(window=base_window).min()) / 2
        leading_span1 = ((conversion_line + base_line) / 2).shift(base_window)
        leading_span2 = (data['high'].rolling(window=(base_window*2)).max() + data['low'].rolling(window=(base_window*2)).min()) / 2

        return conversion_line

    def calculate_elder_ray_index_on_sma(data, window):
        sma = data['close'].rolling(window=window).mean()
        bull_power = data['high'] - sma
        bear_power = data['low'] - sma
        return bull_power, bear_power

    def calculate_elder_ray_index_on_ema(data, window):
        ema = data['close'].ewm(span=window, adjust=False).mean()
        bull_power = data['high'] - ema
        bear_power = data['low'] - ema
        return bull_power, bear_power

    def calculate_ultimate_oscillator(data, short_window, medium_window, long_window):
        avg1 = (data['close'].rolling(window=short_window).sum() /
                data['high'].rolling(window=short_window).sum() * 100)
        avg2 = (data['close'].rolling(window=medium_window).sum() /
                data['high'].rolling(window=medium_window).sum() * 100)
        avg3 = (data['close'].rolling(window=long_window).sum() /
                data['high'].rolling(window=long_window).sum() * 100)
        ultimate_oscillator = ((avg1 * 4) + (avg2 * 2) + avg3) / 7
        return ultimate_oscillator

    def calculate_adaptive_laguerre_filter_volatility(data, gamma, window):

        alpha = np.exp(-gamma)
        lag1 = (1 - alpha) * data['close'] + alpha * data['close'].shift(1)
        lag2 = (-alpha**2) * data['close'] + 2 * alpha * lag1 - lag1.shift(1)
        lag3 = (alpha**3) * data['close'] - 3 * alpha * lag2 + 3 * lag1 - lag1.shift(1)
        lag4 = (-alpha**4) * data['close'] + 4 * alpha * lag3 - 6 * lag2 + 4 * lag1 - lag1.shift(1)
        l0 = (1 - alpha/2)**2 * lag4
        l1 = -2 * (1 - alpha) * lag3
        l2 = (1 - alpha) * (1 - alpha) * lag2
        laguerre = (l0 + l1 + l2) / 6
        volatility = laguerre.diff().abs()

        return laguerre, volatility

    def adaptive_relative_volatility(data, window):
        price_range = data['high'] - data['low']
        average_range = price_range.rolling(window=window).mean()
        adaptive_relative_volatility = (price_range / average_range).rolling(window=window).mean()
        return adaptive_relative_volatility

    def adaptive_wpr_volatility(data, window):
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        price_range = data['high'] - data['low']
        weighted_price_range = price_range * typical_price
        average_weighted_price_range = weighted_price_range.rolling(window=window).mean()
        wpr_volatility = (weighted_price_range / average_weighted_price_range).rolling(window=window).mean()
        return wpr_volatility

    def relative_volatility_index(data, window):
        price_range = data['high'] - data['low']
        smooth_range = price_range.rolling(window=window).mean()
        rvi = (smooth_range / data['close'].shift(1)).cumsum()

        return rvi

    def commodity_selection_index(data, window):
        tr = pd.DataFrame(index=data.index)
        tr['H-L'] = data['high'] - data['low']
        tr['H-PC'] = np.abs(data['high'] - data['close'].shift(1))
        tr['L-PC'] = np.abs(data['low'] - data['close'].shift(1))
        tr['TR'] = tr[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        atr = tr['TR'].rolling(window=window).mean()
        csi = (data['close'] - data['open']) / atr
        return csi

    def demand_index_volatility(data, window):
        di = data['high'] - data['low']
        return di / di.rolling(window=window).sum()

    def efficiency_ratio_volatility(data, window):
        daily_returns = data['close'].pct_change()
        volatility = daily_returns.rolling(window=window).std()
        return 1 / volatility

    def pivot_points_volatility(data):
        pivot_point = (data['high'] + data['low'] + data['close']) / 3
        
        r1 = 2 * pivot_point - data['low']
        s1 = 2 * pivot_point - data['high']
        r2 = pivot_point + (data['high'] - data['low'])
        s2 = pivot_point - (data['high'] - data['low'])
        r3 = pivot_point + 2 * (data['high'] - data['low'])
        s3 = pivot_point - 2 * (data['high'] - data['low'])
        
        return r1, s1, r2, s2, r3, s3

    def cycles_indicator_volatility(data, window):
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        price_change = typical_price - typical_price.shift(window)
        cycles_indicator = price_change.rolling(window=window).std()
        return cycles_indicator

    def darvas_box_volatility(data, window):
        high_shifted = data['high'].shift(window)
        low_shifted = data['low'].shift(window)
        
        upper_band = high_shifted + (high_shifted - low_shifted) / 2
        lower_band = low_shifted - (high_shifted - low_shifted) / 2
        
        darvas_box_volatility = (upper_band - lower_band) / 2
        return darvas_box_volatility

    def calculate_rsi_on_indicators(data, rsi_window):

        data_rsi = data.copy()
        data_rsi = calculate_rsi(data_rsi, 'BB_mid', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'rolling_std', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'BB_high', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'BB_low', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'BB_percentageChange', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'BB_width', rsi_window)    
        data_rsi = calculate_rsi(data_rsi, 'donchian_high', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'donchian_low', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'donchian_mid', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'donchian_percentageChange', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'donchian_width', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'TRANGE', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'ATR', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'NATR', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'close_previous', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'kc_low', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'kc_width', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'typical_price', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'kc_mid', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'kc_high', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'ulcer_index', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'ui_drawdown', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'chaikin_volatility', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'ema_price_spread', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'ROC', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'SMA', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'EMA_no_adjust', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'EMA_adjusted', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'WMA', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'HMA', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'MACD', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'Signal_Line', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'K_percent', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'D_percent', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'CCI_sma', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'CCI_ema', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'DPO_sma', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'DPO_ema', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'Trix_sma', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'Bull_Power_sma', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'Bull_Power_ema', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'Bear_Power_sma', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'Bear_Power_ema', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'Conversion_Line', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'laguerre', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'laguerre_volatility', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'adaptive_relative_volatility', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'adaptive_wpr_volatility', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'RVI', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'demand_index_volatility', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'commodity_selection_index', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'efficiency_ratio_volatility', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'R1', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'R2', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'R3', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'S1', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'S2', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'S3', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'cycles_indicator', rsi_window)
        data_rsi = calculate_rsi(data_rsi, 'darvas_box', rsi_window)
        data_rsi = data_rsi.filter(like='_rsi') 
        return data, data_rsi
       
    def calculate_stoch_on_indicators(data, k_window, d_window):

        data_stoch = data.copy()
        data_stoch = calculate_stoch(data_stoch, 'BB_mid', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'rolling_std', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'BB_high', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'BB_low', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'BB_percentageChange', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'BB_width', k_window, d_window)    
        data_stoch = calculate_stoch(data_stoch, 'donchian_high', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'donchian_low', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'donchian_mid', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'donchian_percentageChange', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'donchian_width', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'TRANGE', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'ATR', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'NATR', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'close_previous', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'kc_low', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'kc_width', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'typical_price', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'kc_mid', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'kc_high', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'ulcer_index', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'ui_drawdown', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'chaikin_volatility', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'ema_price_spread', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'ROC', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'SMA', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'EMA_no_adjust', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'EMA_adjusted', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'WMA', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'HMA', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'MACD', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'Signal_Line', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'CCI_sma', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'CCI_ema', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'DPO_sma', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'DPO_ema', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'Trix_sma', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'Bull_Power_sma', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'Bull_Power_ema', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'Bear_Power_sma', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'Bear_Power_ema', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'Conversion_Line', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'laguerre', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'laguerre_volatility', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'adaptive_relative_volatility', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'adaptive_wpr_volatility', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'RVI', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'demand_index_volatility', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'commodity_selection_index', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'efficiency_ratio_volatility', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'R1', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'R2', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'R3', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'S1', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'S2', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'S3', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'cycles_indicator', k_window, d_window)
        data_stoch = calculate_stoch(data_stoch, 'darvas_box', k_window, d_window)
        data_stoch = data_stoch.filter(regex='k_percent|d_percent')
        return data_stoch
           
    def integrating_indicators(args):

        data, rsi_window, gamma, window, short_window, medium_window, long_window, signal_window, k_window, d_window, \
        bb_window, bb_deviation, donchian_window, keltner_window,\
        ulcer_index_window, atr_window, chaikin_volatility_period, \
        atr_kc_multiplier, dpo_period, roc_period = args

        data['SMA'] = calculate_sma(data, window)
        data['EMA_no_adjust'] = calculate_ema_without_adjust(data, window)
        data['EMA_adjusted'] = calculate_ema_with_adjust(data, window)
        data['WMA'] = calculate_wma(data, window)
        data['HMA'] = calculate_hma(data, window)
        data['MACD'], data['Signal_Line'] = calculate_macd(data, short_window, long_window, signal_window)
        data['K_percent'], data['D_percent'] = calculate_stochastic_oscillator(data, k_window, d_window)
        data['TR'], data['ATR'] = calculate_atr(data, window)
        data['CCI_sma'] = calculate_cci_on_sma(data, window)
        data['CCI_ema'] = calculate_cci_on_ema(data, window)
        data['DPO_sma'] = calculate_detrended_price_oscillator_on_sma(data, window)
        data['DPO_ema'] = calculate_detrended_price_oscillator_on_ema(data, window)
        data['Trix_sma'] = calculate_trix_on_sma(data, window)
        data['Trix_ema'] = calculate_trix_on_ema(data, window)
        data['Bull_Power_sma'], data['Bear_Power_sma'] = calculate_elder_ray_index_on_sma(data, window)
        data['Bull_Power_ema'], data['Bear_Power_ema'] = calculate_elder_ray_index_on_ema(data, window)
        data['Conversion_Line'] = calculate_ichimoku_cloud(data, short_window, long_window)
        data['laguerre'], data['laguerre_volatility'] = calculate_adaptive_laguerre_filter_volatility(data, gamma, window)
        data['adaptive_relative_volatility'] = adaptive_relative_volatility(data, window)
        data['adaptive_wpr_volatility'] = adaptive_wpr_volatility(data, window)
        data['RVI'] = relative_volatility_index(data, window)
        data['demand_index_volatility'] = demand_index_volatility(data, window)
        data['commodity_selection_index'] = commodity_selection_index(data, window)
        data['efficiency_ratio_volatility'] = efficiency_ratio_volatility(data, window)
        data['R1'], data['S1'], data['R2'], data['S2'], data["R3"], data['S3'] = pivot_points_volatility(data)
        data['cycles_indicator'] = cycles_indicator_volatility(data, window)
        data['darvas_box'] = darvas_box_volatility(data, window)
        data['BB_mid'] = data['close'].rolling(window=bb_window).mean()
        data['rolling_std'] = data['close'].rolling(window=bb_window).std()
        data['BB_high'] = data['BB_mid'] + (bb_deviation * data['rolling_std'])
        data['BB_low'] = (data['BB_mid'] - (bb_deviation * data['rolling_std']))
        data['BB_percentageChange'] = (data['close'] - data['BB_mid']) / data['BB_mid']
        data['BB_width'] = data['BB_high'] - data['BB_low']
        data['donchian_high'] = data['high'].rolling(window=donchian_window).max()
        data['donchian_low'] = (data['low'].rolling(window=donchian_window).min())
        data['donchian_mid'] = (data['donchian_high'] + data['donchian_low']) / 2
        data['donchian_percentageChange'] = (data['close'] - (data['donchian_high'] + data['donchian_low']) / 2) / ((data['donchian_high'] + data['donchian_low']) / 2)
        data['donchian_width'] = data['donchian_high'] - data['donchian_low']
        data['close_previous'] = data['close'].shift(1)
        data['TRANGE'] = data.apply(lambda row: max(row['high'] - row['low'],abs(row['high'] - row['close_previous']),abs(row['low'] - row['close_previous'])),axis=1)
        data['ATR'] = data['TRANGE'].rolling(window=atr_window).mean()
        data['NATR'] = (data['ATR'] / data['close']) * 100
        data['typical_price'] = (data['high'] + data['low'] + data['close']) / 3
        data['kc_mid'] = data['typical_price'].rolling(window=keltner_window).mean()
        data['kc_high'] = data['kc_mid'] + (atr_kc_multiplier * data['ATR'])
        data['kc_low'] = data['kc_mid'] - (atr_kc_multiplier * data['ATR'])
        data['kc_width'] = (data['kc_high'] - data['kc_low']) / data['kc_mid']
        data['ui_drawdown'] = 100 * (data['close'] - data['close'].rolling(window=ulcer_index_window).max()) / data['close'].rolling(window=ulcer_index_window).max()
        mean_squared_drawdown = (data['ui_drawdown'] ** 2).rolling(window=ulcer_index_window).mean()
        data['ulcer_index'] = mean_squared_drawdown ** 0.5
        data['price_spread'] = data['high'] - data['low']
        data['ema_price_spread'] = data['price_spread'].ewm(span=chaikin_volatility_period, adjust=False).mean()
        data['chaikin_volatility'] = 100 * (data['price_spread'] - data['ema_price_spread']) / data['ema_price_spread']
        midpoint = (dpo_period // 2) + 1
        data['sma_midpoint'] = data['close'].rolling(window=midpoint).mean()
        data['DPO'] = data['close'] - data['sma_midpoint'].shift(midpoint)
        data['ROC'] = ((data['close'] - data['close'].shift(roc_period)) / data['close'].shift(roc_period)) * 100
        
        data, data_rsi = calculate_rsi_on_indicators(data, rsi_window)
        data_stoch = calculate_stoch_on_indicators(data, k_window, d_window)
        
        return data, data_rsi, data_stoch

    data, data_rsi, data_stoch = integrating_indicators(args)
    

    return data, data_rsi, data_stoch
    


    
    
