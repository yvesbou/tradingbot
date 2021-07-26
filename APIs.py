# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 15:07:51 2020

@author: vinmue
"""
# from binance.client import Client
from poloniex import Poloniex
# from binance.websockets import BinanceSocketManager
import requests
import ast
import math
import hashlib,hmac
import json
import urllib
import time

# todo:
# v3/order?side=BUY

# Best price/qty on the order book for a symbol or symbols:
# /api/v3/ticker/bookTicker?symbol=
# If the symbol is not sent, bookTickers for all symbols will be returned in an array.


class API(object):
    def __init__(self, platform):
        self.platform = platform
        if (self.platform == 'binance'):
            # from account xxx
            self.api_key = "xxx"
            self.api_secret = "xxx"
            # for changing periods in seconds binance accepted strings
            self.period_dict = {60: "1m", 180: "3m", 300: "5m", 900: "15m", 1800: "30m", 3600: "1h", \
                                7200: "2h", 14400: "4h", 21600: "6h", 28800: "8h", 43200: "12h", 86400: "1d", \
                                259200: "3d", 1209600: "1w"}
        elif (self.platform == 'poloniex'):
            # has to be filled in later for private commands
            self.conn = Poloniex('api-key', 'secret')

    def returnTicker(self):
        if (self.platform == 'binance'):
            # returns a list of dictionaries with key symbol and price for each pair
            url="https://api.binance.com/api/v3/ticker/price?"
            for k in range(10):
                try:
                    request = requests.get(url, timeout=1)
                    request.raise_for_status()
                    break
                except:
                    print('request failed')
                    time.sleep(1)
            #request = requests.get("https://api.binance.com/api/v3/ticker/price?")
            # translates request into python datatype
            ticker = request.json()
            # creates a dictionary with the pairs as keys
            dic = {}
            for item in ticker:
                #print(item.keys()[0])
                if ('USDT' in item['symbol'] and 'BTC' in item['symbol']) or ('USDC' in item['symbol'] and 'BTC' in item['symbol']) or\
                        ('BUSD' in item['symbol'] and 'BTC' in item['symbol']):
                    newkey = [item['symbol'][:3], item['symbol'][-4:]]
                    newkey.reverse()
                    newkey = "_".join(newkey)
                    dic[newkey] = {}
                    dic[newkey] = {'last': float(item['price'])}
                elif 'BTC' in item['symbol']:
                    newkey = item['symbol'][-3:], item['symbol'][:-3]
                    newkey = "_".join(newkey)
                    dic[newkey] = {'last': float(item['price'])}
            #ticker = {each.pop('symbol'): each for each in ticker}
            # makes the dictionary to a string to replace price by last to be poloniex compatible and then converts it back to a dictionary

        if (self.platform == 'poloniex'):
            dic = self.conn.returnTicker()
        return dic

    def returnCurrentPrice(self, pair):
        if (self.platform == 'binance'):
            pair = pair.split("_")
            pair.reverse()
            pair = "".join(pair)
            # gives dictionary with keys symbol (pair) and price
            url="https://api.binance.com/api/v3/ticker/price?symbol={}".format(pair)
            for k in range(10):
                try:
                    request = requests.get(url, timeout=1)
                    request.raise_for_status()
                    break
                except:
                    print('request failed')
                    time.sleep(1)
            #request = requests.get("https://api.binance.com/api/v3/ticker/price?symbol={}".format(pair))
            currentPrice = request.json()['price']
        if (self.platform == 'poloniex'):
            currentPrice = self.conn.returnTicker()[pair]['last']
        return currentPrice

    def returnChartData(self, pair, start, end, period):
        # print("here")
        if (self.platform == 'binance'):
            chart_lis = []
            period_str = self.period_dict[period]
            # the pairs are written in poloniex convention with quote_base and therefore have to be reversed
            pair = pair.split("_")
            pair.reverse()
            pair = "".join(pair)
            # binance works with timestamps in miliseconds so our timestamps have to be converted
            start = 1000 * start
            end = 1000 * end
            # split the request in chunks that have in maximum 1000 datapoints
            numParts = math.ceil((end - start) / (period * 1e6))
            print('pair:', pair, 'numparts:', numParts)
            for i in range(numParts):
                subStart = start + i * (end - start) / numParts
                subEnd = start + (i + 1) * (end - start) / numParts
                print('start:', start, 'end:', end, 'subStart:', subStart, 'subEnd:', subEnd)
                url = 'https://api.binance.com/api/v1/klines?symbol={}&interval={}&startTime={}&endTime={}&limit=1000'.format( \
                    pair, period_str, int(subStart), int(subEnd))
                for k in range(10):
                    try:
                        request = requests.get(url, timeout=1)
                        request.raise_for_status()
                        break
                    except:
                        print('request failed')
                        time.sleep(1)
                #request = requests.get(url)
                chart_lis += request.json()

            # chart_lis is a list of lists, highest in hierarchy are the timestamps
            # chart becomes a list of dictionaries, a dictionary for each timestamp
            chart = []
            for i in chart_lis:
                chart.append({})
                chart[-1]['date'] = int(i[0]) / 1000
                chart[-1]['open'] = float(i[1])
                chart[-1]['high'] = float(i[2])
                chart[-1]['low'] = float(i[3])
                chart[-1]['close'] = float(i[4])
                chart[-1]['volume'] = float(i[5])
                chart[-1]['closeTime'] = i[6]
                chart[-1]['quoteAssetVolume'] = i[7]
                chart[-1]['numberOfTrades'] = i[8]
                chart[-1]['takerBuyBaseAssetVolume'] = i[9]
                chart[-1]['takerBuyQuoteAssetVolume'] = i[10]

        if self.platform == 'poloniex':
            chart = self.conn.returnChartData(currencyPair=pair, start=start,
                                              end=end, period=period)
        return chart

    def Buy(self, pair, quantity):
        if self.platform == 'binance':
            pair = pair.split("_")
            pair.reverse()
            pair = "".join(pair)
            for k in range(10):
                try:
                    servertime = requests.get("https://api.binance.com/api/v3/time")
                    servertime.raise_for_status()
                    break
                except:
                    print('request failed')
                    time.sleep(1)

            servertimeobject = json.loads(servertime.text)
            servertimeint = servertimeobject['serverTime']
            params = urllib.parse.urlencode({
                #"recvWindow": 5000,
                #"quantity": quantity,
                #"type": 'MARKET',
                #"side": 'buy',
                #"sympol": pair,
                "timestamp": servertimeint,

            })
            hashedsig = hmac.new(self.api_secret.encode('utf-8'), params.encode('utf-8'),
                                 hashlib.sha256).hexdigest()
            for k in range(10):
                try:
                    request = requests.get("https://api.binance.com/api/v3/order",
                                           params={
                                               "recvWindow": 5000,
                                               "quantity": quantity,
                                               "type": 'MARKET',
                                               "side": 'buy',
                                               "sympol": pair,
                                               "timestamp": servertimeint,
                                               "signature": hashedsig,
                                           },
                                           headers={
                                               "X-MBX-APIKEY": self.api_key,
                                           }
                                           )  # possible status: NEW, PARTIALLY_FILLED, FILLED, CANCELED, PENDING_CANCEL, REJECTED, EXPIRED
                    request.raise_for_status()
                    break
                except:
                    print('request failed')
                    time.sleep(1)

            status = request.json()['status']
            buyPrice = float(request.json()['price'])
            # todo: print the difference between price of our deal vs. ticker price
            return status, buyPrice
        else:
            pass

    def Sell(self, pair, quantity):
        if self.platform == 'binance':
            pair = pair.split("_")
            pair.reverse()
            pair = "".join(pair)
            for k in range(10):
                try:
                    servertime = requests.get("https://api.binance.com/api/v3/time")
                    servertime.raise_for_status()
                    break
                except:
                    print('request failed')
                    time.sleep(1)

            servertimeobject = json.loads(servertime.text)
            servertimeint = servertimeobject['serverTime']
            params = urllib.parse.urlencode({
                #"recvWindow":5000,
                #"quantity":quantity,
                #"type":'MARKET',
                #"side":'sell',
                #"sympol":pair,
                "timestamp": servertimeint,

            })
            hashedsig = hmac.new(self.api_secret.encode('utf-8'), params.encode('utf-8'),
                                 hashlib.sha256).hexdigest()
            for k in range(10):
                try:
                    request = requests.get("https://api.binance.com/api/v3/order",
                                           params={
                                               "recvWindow": 5000,
                                               "quantity": quantity,
                                               "type": 'MARKET',
                                               "side": 'sell',
                                               "sympol": pair,
                                               "timestamp": servertimeint,
                                               "signature": hashedsig,
                                           },
                                           headers={
                                               "X-MBX-APIKEY": self.api_key,
                                           }
                                           )
                    request.raise_for_status()
                    break
                except:
                    print('request failed')
                    time.sleep(1)

            #request = requests.get("https://api.binance.com/api/v3/time")
            #serverTime = request.json()['serverTime']
            #request = requests.get(f"https://api.binance.com/api/v3/order?symbol={pair}&side=sell&type=MARKET&quantity={quantity}&recvWindow=5000&timestamp={serverTime}")
            status = request.json()['status']
            sellPrice = float(request.json()['price'])
            return status, sellPrice
        else:
            pass

    def getBalance(self):
        if self.platform == 'binance':
            for k in range(10):
                try:
                    servertime = requests.get("https://api.binance.com/api/v3/time")
                    servertime.raise_for_status()
                    break
                except:
                    print('request failed')
                    time.sleep(1)


            servertimeobject = json.loads(servertime.text)
            servertimeint = servertimeobject['serverTime']
            params = urllib.parse.urlencode({
                "timestamp": servertimeint,
            })
            hashedsig = hmac.new(self.api_secret.encode('utf-8'), params.encode('utf-8'),
                                 hashlib.sha256).hexdigest()
            for k in range(10):
                try:
                    request = requests.get("https://api.binance.com/api/v3/account",
                                           params={
                                               "timestamp": servertimeint,
                                               "signature": hashedsig,
                                           },
                                           headers={
                                               "X-MBX-APIKEY": self.api_key,
                                           }
                                           )
                    request.raise_for_status()
                    break
                except:
                    print('request failed')
                    time.sleep(1)

            # tempBalances is a list of dictionaries
            tempBalances = request.json()['balances']
            balances = {}
            for dictionary in tempBalances:
                coin = dictionary['asset']
                balance = float(dictionary['free'])
                if float(dictionary['locked']) > 0:
                    print(f"{dictionary['locked']} is locked in coin {coin}")
                balances[coin] = balance
            return balances
        else:
            pass

