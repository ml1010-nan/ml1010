import pandas as pd
from stockstats import StockDataFrame as Sdf
from datetime import datetime, timedelta
from yahoofinancials import YahooFinancials
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats


class Price:
    def __init__(self, date, high, low, open, close, volume, adj_close, formatted_date):
        self.date = date
        self.high = high
        self.low = low
        self.open = open
        self.close = close
        self.volume = volume
        self.adj_close = adj_close
        self.formatted_date = formatted_date
        self.maShort = 0
        self.maLong = 0
        self.label_price = 'N/A'
        self.label_trend = 'N/A'
        self.prev30 = 0.0
        self.prev07 = 0.0
        self.after07 = 0.0
        self.after30 = 0.0
        self.bin_prev30 = 'N/A'
        self.bin_prev07 = 'N/A'
        self.bin_after07 = 'N/A'
        self.bin_after30 = 'N/A'
        self.vol_state = 'N/A'

    def asdict(self):
        return {'date': self.date, 'high': self.high, 'low': self.low,
                'open': self.open, 'close': self.close, 'volume': self.volume,
                'adj_close': self.adj_close, 'formatted_date': self.formatted_date,
                'maShort': self.maShort, 'maLong': self.maLong,
                'label_price': self.label_price, 'label_trend': self.label_trend,
                'prev30': self.prev30, 'prev07': self.prev07, 'after07': self.after07, 'after30': self.after30,
                'bin_prev30': self.bin_prev30, 'bin_prev07': self.bin_prev07,
                'bin_after07': self.bin_after07, 'bin_after30': self.bin_after30,
                'vol_state':self.vol_state}


class PriceHistory:
    def __init__(self, raw_prices, ma_short, ma_long):
        self.ma_short = ma_short
        self.ma_long = ma_long
        prices = raw_prices
        price_list = []
        for price in prices:
            price_list.append(Price(price["date"], price["high"], price["low"], price["open"], price["close"],
                                    price["volume"], price["adjclose"], price["formatted_date"]))
        price_list.sort(key=lambda x: x.date, reverse=True)
        self.PriceHistory = price_list.copy()
        self.PriceFeature = self.assign_ma()

    def get_ma(self, from_index, days):
        end_index = min(len(self.PriceHistory), from_index + days)
        sub_list = self.PriceHistory[from_index: end_index]
        sum_close = 0
        for x in sub_list:
            sum_close += x.close
        return sum_close / days

    def get_label_as_price(self, index):
        next_day_index = index - 1
        if next_day_index >= 0:
            return self.PriceHistory[next_day_index].close
        else:
            return 'N/A'

    def get_label_as_trend(self, index):
        next_day_index = index - 1
        if next_day_index >= 0:
            change = self.PriceHistory[next_day_index].close - self.PriceHistory[index].close
            if change > 0:
                return 'UP'
            elif change == 0:
                return 'NEUTRAL'
            else:
                return 'DOWN'
        else:
            return 'N/A'

    def get_perc_prev(self, index, daydiff):
        next_day_index = index - daydiff
        if next_day_index >= 0:
            change = (self.PriceHistory[index].close - self.PriceHistory[next_day_index].close)/self.PriceHistory[index].close * 100
            return change
        else:
            return -100

    def get_perc_after(self, index, daydiff):
        end_index = len(self.PriceHistory)
        next_day_index = index + daydiff
        if next_day_index < end_index:
            change = (self.PriceHistory[next_day_index].close - self.PriceHistory[index].close)/self.PriceHistory[index].close * 100
            return change
        else:
            return -100

    def get_bin_perc(self, change):

        if change == 0:
            return '0.Neutral'
        elif 5 > change > 0:
            return '1.Low Increase'
        elif 10 > change >= 5:
            return '2.Moderate Increase'
        elif 15 > change >= 10:
            return '3.High Increase'
        elif 20 > change >= 15:
            return '4.Very High Increase'
        elif change >= 20:
            return '5. Extreme Increase'
        elif -5 < change < 0:
            return '-1.Low Decrease'
        elif -10 <= change <= -5:
            return '-2.Moderate Decrease'
        elif -15 <= change <= -5:
            return '-3.High Decrease'
        elif -20 <= change <= -5:
            return '-4.Very High Decrease'
        elif change <= -20:
            return '-5.Extreme Decrease'
        else:
            return 'N/A'

    def get_bin_volume(self, index):

        if self.PriceHistory[index].volume == 0:
            return '0.No Volume'
        elif 30000000 >= self.PriceHistory[index].volume > 0:
            return '1.Low Volume'
        elif 50000000 >= self.PriceHistory[index].volume > 30000000:
            return '2.Moderate Volume'
        elif 80000000 >= self.PriceHistory[index].volume > 50000000:
            return '3.High Volume'
        elif self.PriceHistory[index].volume > 80000000:
            return '4.Extreme Volume'
        else:
            return '-1.N/A'


    def assign_ma(self):
        price_history = self.PriceHistory.copy()
        price_dict_list = []
        for price in price_history:
            price.maShort = self.get_ma(price_history.index(price), self.ma_short)
            price.maLong = self.get_ma(price_history.index(price), self.ma_long)
            price.label_price = self.get_label_as_price(price_history.index(price))
            price.label_trend = self.get_label_as_trend(price_history.index(price))
            price.prev30 = self.get_perc_prev(price_history.index(price), 30)
            price.prev07 = self.get_perc_prev(price_history.index(price), 7)
            price.after30 = self.get_perc_after(price_history.index(price), 30)
            price.after07 = self.get_perc_after(price_history.index(price), 7)
            price.bin_prev30 = self.get_bin_perc(price.prev30)
            price.bin_prev07 = self.get_bin_perc(price.prev07)
            price.bin_after07 = self.get_bin_perc(price.after07)
            price.bin_after30 = self.get_bin_perc(price.after30)
            price.vol_state = self.get_bin_volume(price_history.index(price))
            price_dict = price.asdict().copy()
            price_dict_list.append(price_dict)
        return price_dict_list


class StockPrice:
    def __init__(self, stock, from_date, to_date, ma_short, ma_long):
        self.stock = stock
        self.from_date = from_date
        self.to_date = to_date
        self.ma_short = ma_short
        self.ma_long = ma_long
        # assign prices
        prices = YahooFinancials(stock).get_historical_price_data(from_date, to_date, 'daily')[stock]["prices"]
        self.price_history = PriceHistory(prices, ma_short, ma_long)


ticker = 'AAPL'
to_date = datetime.strftime(datetime.today() - timedelta(days=1), '%Y-%m-%d')
from_date = datetime.strftime(datetime.today() - timedelta(days=2*365), '%Y-%m-%d')

appl = StockPrice(ticker, from_date, to_date, 2, 15)
data = pd.DataFrame(appl.price_history.PriceFeature)
print(data)
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
data['boll_ub'] = stock['boll_ub']
data['boll_lb'] = stock['boll_lb']

plt.interactive(True)

#filtering out of range data
prev30_filter = data.loc[data['prev30'] != -100 ]
prev07_filter = data.loc[data['prev07'] != -100 ]
after07_filter = data.loc[data['after07'] != -100 ]
after30_filter = data.loc[data['after30'] != -100 ]



#prev30_filter graph
prev30_min = prev30_filter['prev30'].min()
prev30_max = prev30_filter['prev30'].max()

for i, binwidth in enumerate([1, 2, 3, 5]):
    # Set up the plot
    p30 = plt.subplot(2, 2, i + 1)

    # Draw the plot
    p30.hist(prev30_filter['prev30'], color='red', edgecolor='red', bins=int(abs(prev30_max - prev30_min)/binwidth))

    # Title and labels
    p30.set_title('Histogram with Binwidth = %d' % binwidth, size=15)
    p30.set_xlabel('Price % change', size=10)
    p30.set_ylabel('Occurance', size=10)



#prev07_filter_graph
prev07_min = prev07_filter['prev07'].min()
prev07_max = prev07_filter['prev07'].max()

for i, binwidth in enumerate([1, 2, 3, 5]):
    # Set up the plot
    p07 = plt.subplot(2, 2, i + 1)

    # Draw the plot
    p07.hist(prev07_filter['prev07'], color='orange', edgecolor='orange', bins=int(abs(prev07_max - prev07_min)/binwidth))

    # Title and labels
    p07.set_title('Histogram with Binwidth = %d' % binwidth, size=15)
    p07.set_xlabel('Price % change', size=10)
    p07.set_ylabel('Occurance', size=10)


#after07_filter_graph
after07_min = after07_filter['after07'].min()
after07_max = after07_filter['after07'].max()

for i, binwidth in enumerate([1, 2, 3, 5]):
    # Set up the plot
    a07 = plt.subplot(2, 2, i + 1)

    # Draw the plot
    a07.hist(after07_filter['after07'], color='yellow', edgecolor='yellow', bins=int(abs(after07_max - after07_min)/binwidth))

    # Title and labels
    a07.set_title('Histogram with Binwidth = %d' % binwidth, size=15)
    a07.set_xlabel('Price % change', size=10)
    a07.set_ylabel('Occurance', size=10)



#after30_filter_graph
after30_min = after30_filter['after30'].min()
after30_max = after30_filter['after30'].max()

for i, binwidth in enumerate([1, 2, 3, 5]):
    # Set up the plot
    a30 = plt.subplot(2, 2, i + 1)

    # Draw the plot
    a30.hist(after30_filter['after30'], color='yellow', edgecolor='yellow', bins=int(abs(after30_max - after30_min)/binwidth))

    # Title and labels
    a30.set_title('Histogram with Binwidth = %d' % binwidth, size=15)
    a30.set_xlabel('Price % change', size=10)
    a30.set_ylabel('Occurance', size=10)



#volume_graph
volume_min = data['volume'].min()
volume_max = data['volume'].max()

for i, binwidth in enumerate([1000000 ,5000000, 10000000, 20000000]):
    # Set up the plot
    vg = plt.subplot(2, 2, i + 1)

    # Draw the plot
    vg.hist(data['volume'], color='purple', edgecolor='purple', bins=int(abs(volume_max - volume_min)/binwidth))

    # Title and labels
    vg.set_title('Histogram with Binwidth = %d' % binwidth, size=15)
    vg.set_xlabel('Price % change', size=10)
    vg.set_ylabel('Occurance', size=10)

#distribution group
prev30_group = prev30_filter[['bin_prev30','prev30']].groupby(['bin_prev30']).agg(['count','mean'])
print(prev30_group)

prev07_group = prev07_filter[['bin_prev07','prev07']].groupby(['bin_prev07']).agg(['count','mean'])
print(prev07_group)

after07_group = after07_filter[['bin_after07','after07']].groupby(['bin_after07']).agg(['count','mean'])
print(after07_group)

after30_group = after30_filter[['bin_after30','after30']].groupby(['bin_after30']).agg(['count','mean'])
print(after30_group)

volume_group = data[['vol_state','volume']].groupby(['vol_state']).agg(['count','mean'])
print(volume_group)


print(data.columns.get_values())



