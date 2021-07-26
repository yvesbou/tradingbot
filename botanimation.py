import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import numpy as np
#import matplotlib.ticker as plticker
import matplotlib
import urllib3
import time
import matplotlib.pyplot as plt

class BotAnimation(object):
    
    def __init__(self,chart,strategy,developingCandlestick,BotCandlestick,pairs,period):
       self.fig,self.ax=plt.subplots(1,2)
       self.indices=['last']
       self.lines=len(self.indices)*[0]
       self.maximum=0
       self.minimum=10000000
       self.times=[]
       self.pairs=pairs
       self.period=period
       self.old_tickers={}
       self.candlesticks=[]
       self.chart=chart
       self.strategy=strategy
       self.developingCandlestick=developingCandlestick
       self.BotCandlestick=BotCandlestick
       plt.setp(self.ax[0].xaxis.get_majorticklabels(),'rotation', 15)
       
       #loc = plticker.MultipleLocator(base=65) # this locator puts ticks at regular intervals
       
       #self.ax[0].xaxis.set_major_locator(loc)
       for it in range(len(self.indices)):
            val=self.indices[it]
            self.lines[it],=self.ax[0].plot_date([], [],lw=1.5,linestyle='-',label=val,color='blue')
            self.old_tickers[val]=[]
       self.ani = FuncAnimation(self.fig, self.update, blit=False, interval=10000)
       plt.show() 
        
    def update(self,i):
        
        currentValues= self.chart.getCurrentValues()
        currentPairPrice=currentValues[self.pair]['last']
        
        #lastPairPrice = currentValues[self.pair]['last']
        self.times.append(datetime.now())
        self.developingCandlestick.tick(currentPairPrice)
        
        '''
        try:
            self.developingCandlestick.tick(currentPairPrice)
    
        except urllib3.URLError:
            time.sleep(int(30))
        '''
        if self.developingCandlestick.isClosed():
            self.candlesticks.append(self.developingCandlestick)
            self.strategy.tick(self.developingCandlestick)
            self.developingCandlestick = self.BotCandlestick(self.period)
            
        for it in range(len(self.indices)):
            
            val=self.indices[it]
            self.old_tickers[val].append(currentValues[self.pair][val])
            #lines[num_i].set_data(np.arange(0,len(old_tickers[i][-1-plot_len:])),old_tickers[i][-1-plot_len:])
            
            
            ### self.lines[it].set_data(np.arange(0,len(self.old_tickers[val])),self.old_tickers[val])
            self.lines[it].set_data(self.times,self.old_tickers[val])
            #ax.set_xticklabels(times[-1-plot_len:])
            if currentValues[self.pair][val] >= self.maximum:
                self.maximum=currentValues[self.pair][val]
            if currentValues[self.pair][val] <= self.minimum:
                self.minimum=currentValues[self.pair][val]
            
        #print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) + " Period: {}s {} {}".format(self.period, self.pair,lastPairPrice))
                
        
        self.ax[0].set_ylim(self.minimum-2,self.maximum+2)
        self.ax[0].set_xlim(self.times[0],self.times[-1])
        loc = matplotlib.dates.AutoDateLocator(minticks=1,maxticks=5)
        form = matplotlib.dates.AutoDateFormatter(loc)
        self.ax[0].xaxis.set_major_locator(loc)
        self.ax[0].xaxis.set_major_formatter(form)
        return self.lines