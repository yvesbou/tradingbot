# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 15:07:51 2020

@author: vinmue
"""

from poloniex import Poloniex
import pandas
import requests
import ast
import math


class BotApi(object):
    def __init__(self,platform):
        self.platform=platform
        if(self.platform=='binance'):
            # from account xxx@gmail.com
            self.api_key="xxx"
            self.api_secret="xxx"
            # for changing periods in seconds binance accepted strings
            self.period_dict={60:"1m",180:"3m",300:"5m",900:"15m",1800:"30m",3600:"1h",\
                                 7200:"2h",14400:"4h",21600:"6h",28800:"8h",43200:"12h",86400:"1d",\
                                 259200:"3d",1209600:"1w"}
        elif(self.platform=='poloniex'):
            # has to be filled in later for private commands
            self.conn = Poloniex('api-key', 'secret')
            
    def returnTicker(self):
        if(self.platform=='binance'):
            # returns a list of dictionaries with key symbol and price for each pair
           request=requests.get("https://api.binance.com/api/v3/ticker/price?")
           # translates request into python datatype
           ticker=request.json()
            # creates a dictionary with the pairs as keys
           ticker={each.pop('symbol'): each for each in ticker}
            # makes the dictionary to a string to replace price by last to be poloniex compatible and then converts it back to a dictionary
           ticker_str=str(ticker)
           ticker_str=ticker_str.replace("price","last")
           ticker=ast.literal_eval(ticker_str)
        if(self.platform=='poloniex'):
            ticker=self.conn.returnTicker()
        return ticker

    def returnCurrentPrice(self,pair):
        if(self.platform=='binance'):
            pair=pair.split("_")
            pair.reverse()
            pair="".join(pair)
            # gives dictionary with keys symbol (pair) and price
            request=requests.get("https://api.binance.com/api/v3/ticker/price?symbol={}".format(pair))
            currentPrice=request.json()['price']
        if(self.platform=='poloniex'):
            currentPrice=self.conn.returnTicker()[pair]['last']
        return currentPrice
    
    def returnChartData(self,pair,start,end,period):
        #print("here")
        if(self.platform=='binance'):
            chart_lis=[]
            period_str=self.period_dict[period]
            # the pairs are written in poloniex convention with quote_base and therefore have to be reversed
            pair=pair.split("_")
            pair.reverse()
            pair="".join(pair)
            # binance works with timestamps in miliseconds so our timestamps have to be converted
            start=1000*start
            end=1000*end
           # split the request in chunks that have in maximum 1000 datapoints
            numParts=math.ceil((end-start)/(period*1e6))
            print('pair:',pair,'numparts:',numParts)
            for i in range(numParts):
                subStart=start+i*(end-start)/numParts
                subEnd=start+(i+1)*(end-start)/numParts
                print('start:',start,'end:',end,'subStart:',subStart,'subEnd:',subEnd)
                url = 'https://api.binance.com/api/v1/klines?symbol={}&interval={}&startTime={}&endTime={}&limit=1000'.format(\
                  pair,period_str,int(subStart),int(subEnd))
                request=requests.get(url)
                chart_lis+=request.json()
            
          
            # chart_lis is a list of lists, highest in hierarchy are the timestamps
            # chart becomes a list of dictionaries, a dictionary for each timestamp
            chart=[]
            for i in chart_lis:
                chart.append({})
                chart[-1]['date']=int(i[0])/1000
                chart[-1]['open']=float(i[1])
                chart[-1]['high']=float(i[2])
                chart[-1]['low']=float(i[3])
                chart[-1]['close']=float(i[4])
                chart[-1]['volume']=float(i[5])
                chart[-1]['closeTime']=i[6]
                chart[-1]['quoteAssetVolume']=i[7]
                chart[-1]['numberOfTrades']=i[8]
                chart[-1]['takerBuyBaseAssetVolume']=i[9]
                chart[-1]['takerBuyQuoteAssetVolume']=i[10]
                
            
        if(self.platform=='poloniex'):
            
            chart=self.conn.returnChartData(currencyPair=pair, start=start,
                                                 end=end, period=period)
        return chart
    
    def chartToCsv(self,pair,start,end,period):
        #print("here")
        if(self.platform=='binance'):
            chart_lis=[]
            period_str=self.period_dict[period]
            # the pairs are written in poloniex convention with quote_base and therefore have to be reversed
            pair=pair.split("_")
            pair.reverse()
            pair="".join(pair)
            # binance works with timestamps in miliseconds so our timestamps have to be converted
            start=1000*start
            end=1000*end
           # split the request in chunks that have in maximum 1000 datapoints
            numParts=math.ceil((end-start)/(period*1e6))
            print('pair:',pair,'numparts:',numParts)
            for i in range(numParts):
                subStart=start+i*(end-start)/numParts
                subEnd=start+(i+1)*(end-start)/numParts
                print('start:',start,'end:',end,'subStart:',subStart,'subEnd:',subEnd)
                url = 'https://api.binance.com/api/v1/klines?symbol={}&interval={}&startTime={}&endTime={}&limit=1000'.format(\
                  pair,period_str,int(subStart),int(subEnd))
                request=requests.get(url)
                chart_lis+=request.json()
            
          
            # chart_lis is a list of lists, highest in hierarchy are the timestamps
            # chart becomes a list of dictionaries, a dictionary for each timestamp
            chart=[]
            for i in chart_lis:
                chart.append({})
                chart[-1]['date']=int(i[0])/1000
                chart[-1]['open']=float(i[1])
                chart[-1]['high']=float(i[2])
                chart[-1]['low']=float(i[3])
                chart[-1]['close']=float(i[4])
                chart[-1]['volume']=float(i[5])
                chart[-1]['closeTime']=i[6]
                chart[-1]['quoteAssetVolume']=i[7]
                chart[-1]['numberOfTrades']=i[8]
                chart[-1]['takerBuyBaseAssetVolume']=i[9]
                chart[-1]['takerBuyQuoteAssetVolume']=i[10]
            
            
        if(self.platform=='poloniex'):
            
            chart=self.conn.returnChartData(currencyPair=pair, start=start,
                                                 end=end, period=period)
        return chart
