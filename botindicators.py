import numpy as np


class BotIndicators(object):
    def __init__(self, period, pairs):
        self.typicalPrices = {}
        self.moneyFlows = {}
        self.positive_moneyFlow = []
        self.negative_moneyFlow = []
        self.period = period
        self.MA = 0
        for pair in pairs:
            self.typicalPrices[pair] = []
            self.moneyFlows[pair] = []

    def movingAverage(self, closes, dates, pair, length):
        # average gets calculated if there are more than length values in closes
        self.MA = 0
        if len(closes) > length:
            for date in dates[-length:]:
                self.MA += closes[date][pair]
        self.MA /= length
        return self.MA

    def moneyFlowIndex(self, period, dates, highs, lows, closes, volumes, pair):
        '''
        :param period: difference in seconds between two timestamps
        :param dates: timestamp happened so far (in unix-stamps)
        :param highs: highest values of each candlestick
        :param lows: low values of each candlestick
        :param closes: close values of each candlestick
        :param volumes: volume values of each candlestick
        :param pair: pair
        :return: MFI if there is more than one element in positive or negative money-flow
        '''
        high = None
        low = None
        volume = 0
        self.typicalPrices[pair] = []
        self.moneyFlows[pair] = []
        self.positive_moneyFlow = []
        self.negative_moneyFlow = []
        # we want the latest timestamp with index 0
        dates_c = dates.copy()
        dates_c.reverse()
        # how many candlesticks are in one day
        jump = int(86400 / period)

        # loop through all full days
        for i in range(jump, len(dates), jump):
            # loop through all candlesticks of full day and get the highest and lowest value overall candlesticks of that day
            for date in dates_c[i - jump:i]:
                if high is None or highs[date][pair] > high:
                    high = highs[date][pair]
                if low is None or lows[date][pair] < low:
                    low = lows[date][pair]
                volume += volumes[date][pair]

            close = closes[date][pair]

            # calculate typical Price
            typicalPrice = (high + low + close) / 3
            self.typicalPrices[pair].append(typicalPrice)
            moneyFlow = typicalPrice * volume
            self.moneyFlows[pair].append(moneyFlow)

            # if there are at least 15 typical Prices the + and - money flow can be calculated
            if len(self.typicalPrices[pair]) == 15:
                for i, el in enumerate(self.typicalPrices[pair]):
                    if i == 0:
                        pass
                    elif self.typicalPrices[pair][i] > self.typicalPrices[pair][i - 1]:
                        self.positive_moneyFlow.append(self.moneyFlows[pair][i])

                    elif self.typicalPrices[pair][i] < self.typicalPrices[pair][i - 1]:
                        self.negative_moneyFlow.append(self.moneyFlows[pair][i])

                    else:
                        pass

                positive_moneyFlow = sum(self.positive_moneyFlow)
                negative_moneyFlow = sum(self.negative_moneyFlow)
                if positive_moneyFlow + negative_moneyFlow == 0:
                    return None
                MFI = 100 * positive_moneyFlow / (positive_moneyFlow + negative_moneyFlow)
                self.typicalPrices[pair] = []
                self.moneyFlows[pair] = []
                self.positive_moneyFlow = []
                self.negative_moneyFlow = []

                return MFI

    def MACD_Histogram(self, period, dates, closes, pair):

        EMA12_candidates = []
        EMA26_candidates = []
        EMA12 = []
        EMA26 = []
        MACD_Signal_Line = []

        dates_c = dates.copy()
        dates_c.reverse()
        jump = int(86400 / period)

        # loop through all full days
        for i in range(jump, len(dates), jump):
            # loop through all candlesticks of full day and get the highest and lowest value overall candlesticks of that day
            for date in dates_c[i - jump:i]:
                EMA26_candidates.append(closes[date][pair])
                EMA12_candidates.append(closes[date][pair])

        EMA12_candidates.reverse()
        EMA26_candidates.reverse()

        # 12EMA: calculate 12 period Exponential moving average (EMA)
        # 26EMA: calculate 26 period EMA

        for i, el in enumerate(EMA12_candidates):
            if i < 1:
                start = el
                #EMA12.append(start)
                continue
            EMA = (el - start) * (2 / 13) + start
            EMA12.append(EMA)
            start = EMA

        for i, el in enumerate(EMA26_candidates):
            if i < 1:
                start = el
                #EMA26.append(start)
                continue
            EMA = (el - start) * (2 / 27) + start
            EMA26.append(EMA)
            start = EMA

        # MACD: 12EMA minus 26EMA
        EMA12 = np.array(EMA12)
        EMA26 = np.array(EMA26)
        MACD = EMA12[1:] - EMA26[1:]

        # MACD Signal Line: 9 period EMA of MACD

        for i, el in enumerate(MACD):
            if i < 1:
                start = el
                #MACD_Signal_Line.append(start)
                continue
            EMA = (el - start) * (2 / 10) + start
            MACD_Signal_Line.append(EMA)
            start = EMA

        # MACD_Histogram: MACD minus MACD Signal Line
        MACD_Signal_Line = np.array(MACD_Signal_Line)
        MACD_Histogram = MACD[1:] - MACD_Signal_Line

        return MACD_Histogram
