# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 22:28:56 2020

@author: vinmue
"""

from plotly import express

class BotPlot(object):
    def __init__(self,data):
        self.data=data
    def histogram(self,data):
        fig=express.histogram(data_frame=self.data,x="netYield")
        fig.show()
        