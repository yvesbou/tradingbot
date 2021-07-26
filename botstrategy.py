from botindicators import BotIndicators
from bottrade import BotTrade
import time


# from botlog import BotLog


class BotStrategy(object):
    def __init__(self, period, log, api, checker, stopLoss=0, startBalance=100):
        self.highs = {}
        self.lows = {}
        self.closes = {}
        self.dates = []
        self.volumes = {}
        self.MFIs = {}
        self.MACD = {}
        self.MovingAverage = {}
        self.output = log
        self.api = api

        self.pairs = checker.pairs

        self.coins = checker.coins
        self.indicators = BotIndicators(period, self.pairs)
        # unused, but find application
        self.stopLoss = stopLoss
        # todo: self.balance gets info by /api/v3/account
        # self.balance = {i: 0 for i in checker.coins} # disable (it has to be in the tick method below)

        # setting start values for USDT
        #self.balance['USDT'] = startBalance  # todo: disable if livetrading with real money

        # todo: ovr value sums the value got by api/v3/account
        self.oldValue = 0
        self.ovrValue = 0

        self.MFIs = {}
        self.MovingAverage = {}
        self.MFI = None

        self.period = period
        self.counter = 0

    def tick(self, history, timestamp, initialize_live):

        # are all dictionaries, with timestamp as 1st level key and pair becomes 2nd level key (nested dictionary)
        self.highs[timestamp] = {}
        self.lows[timestamp] = {}
        self.closes[timestamp] = {}
        self.dates.append(timestamp)
        self.volumes[timestamp] = {}
        self.MFIs[timestamp] = {}
        self.MovingAverage[timestamp] = {}
        self.MACD[timestamp] = {}

        for pair in self.pairs:
            self.highs[timestamp][pair] = history[timestamp][pair]['high']
            self.lows[timestamp][pair] = history[timestamp][pair]['low']
            self.closes[timestamp][pair] = history[timestamp][pair]['close']
            self.volumes[timestamp][pair] = history[timestamp][pair]['volume']

            self.MovingAverage[timestamp][pair] = self.indicators.movingAverage(closes=self.closes, dates=self.dates,
                                                                                pair=pair, length=5)

            self.MFI = self.indicators.moneyFlowIndex(period=self.period, dates=self.dates,
                                                      highs=self.highs, lows=self.lows,
                                                      closes=self.closes,
                                                      volumes=self.volumes, pair=pair)
            self.MFIs[timestamp][pair] = self.MFI

            self.MACD[timestamp][pair] = self.indicators.MACD_Histogram(period=self.period, dates=self.dates,
                                                                        closes=self.closes, pair=pair)
        if not initialize_live:
            self.evaluatePositions(timestamp)
            self.giveInfo()

    def evaluatePositions(self, timestamp):
        # self.balances is a dictionary with balance for each coin
        self.balances = self.api.getBalance()
        BuyOptions = []
        SellOptions = []
        list_of_trades = []
        notTraded = []
        # latest overall value becomes old value

        self.oldValue = self.ovrValue
        self.ovrValue = 0

        # loops through pairs and checks if MFI indicates a buy or sell option
        for pair in self.pairs:
            if self.MFIs[timestamp][pair]:
                if self.MFIs[timestamp][pair] < 30:
                    BuyOptions.append((pair, self.MFIs[timestamp][pair]))
                if self.MFIs[timestamp][pair] > 70:
                    SellOptions.append(pair)

            # buy if MACD overtakes MACD Signal Line, sell if MACD gets overtaken by MACD Signal Line
            if len(self.MACD[timestamp][pair]) > int(86400 / self.period):
                if (0 > self.MACD[timestamp][pair][-2]) and (self.MACD[timestamp][pair][-1] > 0):
                    # BuyOptions.append(pair)
                    print("According to MACD buy!", self.MACD[timestamp][pair][-2], self.MACD[timestamp][pair][-1],
                          pair)
                if (0 < self.MACD[timestamp][pair][-2]) and (self.MACD[timestamp][pair][-1] < 0):
                    # SellOptions.append(pair)
                    print("According to MACD sell!", self.MACD[timestamp][pair][-2], self.MACD[timestamp][pair][-1],
                          pair)

        # sorts the definitive buy options starting with lowest MFI and takes the 5 with lowest MFI
        # todo: used for MFI, improve by spliting the money to different coins, somehow a voting system by different indicators
        definitiveBuyOptions = sorted(BuyOptions, key=lambda tup: tup[1])[:5]
        # definitiveBuyOptions = BuyOptions
        ## definitiveSellOptions.append(sorted(BuyOptions,key=lambda tup:tup[1])[-5:])
        ## definitiveSellOptions=sorted(BuyOptions,key=lambda tup:tup[1])

        # takes all Sell options as definitive (can be further improved)
        definitiveSellOptions = SellOptions
        print(definitiveBuyOptions)
        print('MFIs:', self.MFIs[timestamp])
        counter = 0
        for sell in definitiveSellOptions:
            coin0 = sell.split("_")[0]
            coin1 = sell.split("_")[1]

            if self.balances[coin1] == 0:
                print(f"Would have sold but no coins of this currency, {sell}")
                continue
            else:
                counter += 1
                # "symbol=BTCUSDC&side=sell&type=LIMIT&quantity=1&recvWindow=5000&timestamp=servertime"
                status, sellPrice = self.api.Sell(pair=sell, quantity=self.balances[coin1])
                if status == "FILLED":
                    list_of_trades.append(status)
                    print(f'sold {sell} at {sellPrice}')
                else:
                    notTraded.append(status, pair)
                    print(status, pair)

        # if there is any buy option, only the best option should be taken
        if len(definitiveBuyOptions) > 1:
            number_of_buys = len(definitiveBuyOptions)
            fraction = 1 / number_of_buys
            buy = []
            buyFraction = {}
            for i, pair in enumerate(definitiveBuyOptions):
                pair=pair[0]
                buy.append(pair)
                buyFraction[pair] = fraction

                split = buy[i].split("_")
                coin0 = split[0]
                coin1 = split[1]


                if self.balances[coin0] == 0:
                    print(f"Would have bought but no coins (BTC (or USDT)) to buy this currency, {pair}")
                    continue
                else:
                    counter += 1
                    # "symbol=BTCUSDC&side=sell&type=LIMIT&quantity=1&recvWindow=5000&timestamp=servertime"
                    status, buyPrice = self.api.Buy(pair=pair, quantity=self.balances[coin1] * buyFraction[pair])
                    if status == "FILLED":
                        list_of_trades.append(status)
                        print(f'bought {pair} at {buyPrice}')
                    else:
                        notTraded.append((status, pair))
                        print(status, pair)

            # evaluate the portfolio value called overall

        if len(list_of_trades) == counter:
            self.balances = self.api.getBalance()
        else:
            print(f'{notTraded} is the list of not Traded pairs')
            time.sleep(10)
            print(f'{notTraded} is the list of not Traded pairs after additional 10 seconds, however the balance gets estimated now!')
            self.balances = self.api.getBalance()

        for pair in self.pairs:

            split = pair.split('_')
            coin0 = split[0]
            coin1 = split[1]

            # MANA / BTC ist bei uns BTC_MANA in api MANABTC
            # 'USDC_BTC' api BTCUSDC

            if coin0 != "USDT" and coin0 != "BTC":
                self.ovrValue += self.balances[coin0] * (1 / self.closes[timestamp][pair]) * self.closes[timestamp]['USDT_BTC']
            if coin1 != "USDT" and coin1 != "BTC":
                self.ovrValue += self.balances[coin1] * self.closes[timestamp][pair] * self.closes[timestamp]['USDT_BTC']
        self.ovrValue += self.balances['USDT']
        self.ovrValue += self.balances['BTC'] * self.closes[timestamp]['USDT_BTC']
        print('USDT:', self.balances['USDT'], 'BTC:', self.balances['BTC'], 'overall value:', self.ovrValue)
        self.counter += self.period

    def giveInfo(self):
        Yield = self.ovrValue - self.oldValue
        print("The overall Value is:" + str(self.ovrValue) + "The yield is: " + str(Yield))
        print("{} days passed".format(self.counter / 86400))
