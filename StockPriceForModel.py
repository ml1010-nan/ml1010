from yahoofinancials import YahooFinancials
import pandas as pd
from stockstats import StockDataFrame as Sdf


class PriceForModel:
    def __init__(self, date, high, low, open, close, volume, adj_close, formatted_date):
        self.date = date
        self.high = high
        self.low = low
        self.open = open
        self.close = close
        self.volume = volume
        self.adj_close = adj_close
        self.formatted_date = formatted_date
        self.label_price = 'NaN'
        self.label_trend = 'NaN'

    def asdict(self):
        return {'date': self.formatted_date, 'high': self.high, 'low': self.low,
                'open': self.open, 'close': self.close, 'volume': self.volume,
                'adj_close': self.adj_close, 'formatted_date':self.formatted_date,
                'label_price': self.label_price, 'label_trend': self.label_trend}


class PriceHistoryForModel:
    def __init__(self, raw_prices, ma_short, ma_long):
        self.ma_short = ma_short
        self.ma_long = ma_long
        prices = raw_prices
        price_list = []
        for price in prices:
            price_list.append(PriceForModel(price["date"], price["high"], price["low"], price["open"], price["close"],
                                    price["volume"], price["adjclose"], price["formatted_date"]))
        self.PriceHistory = price_list.copy()
        self.PriceFeature = self.assign_label()

    def get_label_as_price(self, index):
        next_day_index = index + 1
        if next_day_index < len(self.PriceHistory):
            return self.PriceHistory[next_day_index].close
        else:
            return 'NaN'

    def get_label_as_trend(self, index):
        next_day_index = index + 1
        if next_day_index < len(self.PriceHistory):
            change = self.PriceHistory[next_day_index].close - self.PriceHistory[index].close
            if change > 0:
                return 'UP'
            elif change == 0:
                return 'NEUTRAL'
            else:
                return 'DOWN'
        else:
            return 'NaN'

    def assign_label(self):
        price_history = self.PriceHistory.copy()
        price_dict_list = []
        for price in price_history:
            price.label_price = self.get_label_as_price(price_history.index(price))
            price.label_trend = self.get_label_as_trend(price_history.index(price))
            price_dict = price.asdict().copy()
            price_dict_list.append(price_dict)
        return price_dict_list


class StockPriceForModel:
    def __init__(self, stock, from_date, to_date, ma_short, ma_long):
        self.stock = stock
        self.from_date = from_date
        self.to_date = to_date
        self.ma_short = ma_short
        self.ma_long = ma_long
        # assign prices
        prices = YahooFinancials(stock).get_historical_price_data(from_date, to_date, 'daily')[stock]["prices"]
        self.price_history = PriceHistoryForModel(prices, ma_short, ma_long)
        data = pd.DataFrame(self.price_history.PriceFeature)
        # Append technical indicators into feature dataframe
        stock = Sdf.retype(data)

        data['volume_delta'] = stock['volume_delta']
        data['open_-2_r'] = stock['open_-2_r']

        data['cr-ma1'] = stock['cr-ma1']
        data['cr-ma2'] = stock['cr-ma2']
        data['cr-ma3'] = stock['cr-ma3']
        data['cr-ma2_xu_cr-ma1_20_c'] = stock['cr-ma2_xu_cr-ma1_20_c']

        data['volume_-3,2,-1_max'] = stock['volume_-3,2,-1_max']
        data['volume_-3~1_min'] = stock['volume_-3~1_min']

        data['kdjk'] = stock['kdjk']
        data['kdjd'] = stock['kdjd']
        data['kdjj'] = stock['kdjj']

        data['close_2_sma'] = stock['close_2_sma']
        data['close_5_sma'] = stock['close_5_sma']
        data['close_20_sma'] = stock['close_20_sma']
        data['close_50_sma'] = stock['close_50_sma']
        data['close_200_sma'] = stock['close_200_sma']

        data['rsi_6'] = stock['rsi_6']
        data['rsi_12'] = stock['rsi_12']

        data['wr_10'] = stock['wr_10']
        data['wr_6'] = stock['wr_6']

        # CCI, default to 14 days
        data['cci'] = stock['cci']
        # 20 days CCI
        data['cci_20'] = stock['cci_20']

        # TR (true range)
        data['tr'] = stock['tr']
        # ATR (Average True Range)
        data['atr'] = stock['atr']

        # DMA, difference of 10 and 50 moving average
        data['dma'] = stock['dma']

        # DMI
        # +DI, default to 14 days
        data['pdi'] = stock['pdi']
        # -DI, default to 14 days
        data['mdi'] = stock['mdi']
        # DX, default to 14 days of +DI and -DI
        data['dx'] = stock['dx']
        # ADX, 6 days SMA of DX, same as stock['dx_6_ema']
        data['adx'] = stock['adx']
        # ADXR, 6 days SMA of ADX, same as stock['adx_6_ema']
        data['adxr'] = stock['adxr']
        # TRIX, default to 12 days
        data['trix'] = stock['trix']
        # MATRIX is the simple moving average of TRIX
        data['trix_9_sma'] = stock['trix_9_sma']
        # VR, default to 26 days
        data['vr'] = stock['vr']
        # MAVR is the simple moving average of VR
        data['vr_6_sma'] = stock['vr_6_sma']

        # MACD
        data['macd'] = stock['macd']
        # MACD signal line
        data['macds'] = stock['macds']
        # MACD histogram
        data['macdh'] = stock['macdh']

        # bolling, including upper band and lower band
        data['boll'] = stock['boll']
        data = data.drop(columns=['label_trend'])
        data = data[data.label_price != 'NaN']
        self.price_features = data
