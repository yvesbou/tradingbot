import pandas as pd
# from poloniex import Poloniex
from botcandlestick import BotCandlestick
# from botlog import BotLog
import time


class BotChart(object):

    def __init__(self, period, log, api, checker):
        self.checker = checker
        self.pairs = self.checker.pairs
        self.period = period

        self.output = log
        self.api = api
        self.doubles = []  # list to prevent kickout twice leading to error

    def loadHistory(self, startTime_timestamp, endTime_timestamp, firstTime, duringLive):
        self.history = {}
        self.data = {}
        self.timestamps = []
        # makes sure that the length of the longest history is decisive
        maxLen = -1
        making_timestamps = True
        for pair in self.pairs:
            self.history[pair] = self.api.returnChartData(pair=pair, start=startTime_timestamp,
                                                          end=endTime_timestamp, period=self.period)

            # loop distills the pair with the history with most timestamps and collects the timestamps in a list
            for i, element in enumerate(self.history[pair]):
                timestamp = int(element['date'])
                if len(self.history[pair]) > maxLen:
                    maxLen = len(self.history[pair])
                    making_timestamps = True
                    self.timestamps = []
                if making_timestamps:
                    self.timestamps.append(timestamp)
            making_timestamps = False
            print(len(self.timestamps), len(self.history[pair]), 'maxLen:', maxLen)

        # takes only history of pairs with the maximum length (distilled above) and kicks out pairs with less data
        if firstTime:
            for pair in self.pairs:
                if len(self.history[pair]) != len(self.timestamps):
                    self.checker.mark(pair)
            self.checker.kickOut()

        # fills self.data with data from the history and changes the hierarchy, timestamp becomes 1st level key
        for i, timestamp in enumerate(self.timestamps):
            self.data[timestamp] = {}
            if not duringLive:
                for pair in self.pairs:
                    self.data[timestamp][pair] = self.history[pair][i]
            if duringLive:
                for pair in self.pairs:
                    self.data[timestamp][pair] = self.history[pair][0]


        #self.data.pop(self.timestamps[0])

        return self.data, self.timestamps

    def getCurrentPrice(self, pair):
        lastPairPrice = self.api.getCurrentPrice(pair)
        return lastPairPrice

    def getCurrentTicker(self):
        currentTicker = self.api.returnTicker()
        return currentTicker

