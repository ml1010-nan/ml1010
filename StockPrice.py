from yahoofinancials import YahooFinancials


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
        self.ma20 = 0
        self.ma50 = 0
        self.ma200 = 0


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

    def assign_ma(self):
        price_history = self.PriceHistory.copy()
        for price in price_history:
            price.maShort = self.get_ma(price_history.index(price), self.ma_short)
            price.maLong = self.get_ma(price_history.index(price), self.ma_long)
            price.ma20 = self.get_ma(price_history.index(price), 20)
            price.ma50 = self.get_ma(price_history.index(price), 50)
            price.ma200 = self.get_ma(price_history.index(price), 200)
        return price_history


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


appl = StockPrice('AAPL', '2015-01-15', '2017-10-15', 2, 15)
print(appl.price_history.PriceFeature)

