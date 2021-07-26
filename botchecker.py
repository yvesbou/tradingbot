# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 17:49:42 2020

@author: vinmue
"""
import re
import sys


class BotChecker(object):
    def __init__(self, platform):

        # only USDT pairs
        if (platform == 'poloniex'):
            self.pairs = [
                'BTC_DASH', 'BTC_DOGE', 'BTC_LTC', 'BTC_XEM', 'BTC_XRP', \
                'USDT_BTC', 'BTC_ETH', \
                'BTC_SC', 'BTC_DCR', 'BTC_LSK', 'BTC_STEEM', 'BTC_ETC', \
                'BTC_REP', 'BTC_ARDR', 'BTC_ZEC', \
                'BTC_STRAT', 'BTC_GNT', 'BTC_ZRX', 'BTC_CVC', \
                'BTC_OMG', 'BTC_STORJ', 'BTC_EOS', 'BTC_SNT', \
                'BTC_KNC', 'BTC_BAT', 'BTC_LOOM', \
                'BTC_QTUM', \
                'USDC_BTC', 'BTC_MANA', 'BTC_BNT', \
                'BTC_POLY', 'BTC_ATOM', \
                'BTC_TRX', \
                'BTC_LINK', 'BTC_XTZ', \
                'PAX_BTC', 'BTC_SNX', \
                'BTC_MATIC', 'BTC_MKR', \
                'DAI_BTC', 'BTC_NEO', \
                'BTC_AVA', 'BTC_CHR', \
                'BNB_BTC', \
                'BUSD_BTC', 'BTC_MDT', \
                'BTC_LEND', 'BTC_REN', \
                'BTC_LRC', \
                'BTC_WRX', 'BTC_SXP', \
                'BTC_STPT']

        elif (platform == 'binance'):

            self.pairs = ['BTC_DASH', 'BTC_DOGE', 'BTC_LTC', 'BTC_XEM', 'BTC_XRP', 'USDT_BTC', 'BTC_ETH',
                          'BTC_SC', 'BTC_DCR', 'BTC_LSK', 'BTC_STEEM', 'BTC_ETC', 'BTC_REP', 'BTC_ARDR',
                          'BTC_ZEC', 'BTC_STRAT', 'BTC_GNT', 'BTC_ZRX', 'BTC_CVC', 'BTC_OMG', 'BTC_STORJ',
                          'BTC_EOS', 'BTC_SNT', 'BTC_KNC', 'BTC_BAT', 'BTC_LOOM', 'BTC_QTUM', 'USDC_BTC',
                          'BTC_MANA', 'BTC_BNT', 'BTC_POLY', 'BTC_ATOM', 'BTC_TRX', 'BTC_LINK', 'BTC_XTZ',
                          'BTC_PAX', 'BTC_SNX', 'BTC_MATIC', 'BTC_MKR', 'BTC_DAI', 'BTC_NEO', 'BTC_AVA',
                          'BTC_CHR', 'BTC_BNB', 'BUSD_BTC', 'BTC_MDT', 'BTC_LEND', 'BTC_REN', 'BTC_LRC',
                          'BTC_WRX', 'BTC_SXP', 'BTC_STPT']

        self.coins = ['DASH', 'DOGE', 'LTC', 'XEM', 'XRP', 'USDT', 'BTC', 'ETH', 'SC', 'DCR', 'LSK', 'STEEM', 'ETC',
                      'REP', 'ARDR', \
                      'ZEC', 'STRAT', 'GNT', 'ZRX', 'CVC', 'OMG', 'STORJ', 'EOS', 'SNT', 'KNC', 'BAT', 'LOOM', 'QTUM',
                      'USDC', 'MANA', \
                      'BNT', 'POLY', 'ATOM', 'TRX', 'LINK', 'XTZ', 'PAX', 'SNX', 'MATIC', 'MKR', 'DAI', 'NEO', 'AVA',
                      'CHR', 'BNB', 'BUSD', \
                      'MDT', 'LEND', 'REN', 'LRC', 'WRX', 'SXP', 'STPT']
        self.wastedPairs = []
        self.wastedCoins = []

    def mark(self, pair):
        self.wastedPairs.append(pair)
        print(pair)
        if pair == 'USDT_BTC':
            print('USDT_BTC got kicked out')
            sys.exit(2)

    def kickOut(self):
        for pair in self.wastedPairs:
            self.pairs.remove(pair)


# all coins and pairs from poloniex kept as reserve, someday maybe add binance coins
'''
 self.coins = ['BTC', 'DASH', 'DOGE', 'LTC', 'XEM', 'XRP', 'USDT', 'ETH', 'SC', 'DCR', 'LSK', 'STEEM', 'ETC',
                      'REP', \
                      'ARDR', 'ZEC', 'STRAT', 'ZRX', 'GNT', 'ZRX', 'CVC', 'OMG', 'STORJ', 'EOS', 'SNT', 'KNC', 'BAT',
                      'LOOM', \
                      'QTUM', 'USDC', 'MANA', 'BNT', 'POLY', 'ATOM', 'TRX', 'BTT', 'WIN', 'STEEM', 'LINK', 'XTZ', 'PAX', \
                      'SNX', 'MATIC', 'MKR', 'DAI', 'NEO', 'BTT', 'AVA', 'CHR', 'BNB', 'BUSD', 'MDT', 'COMP', 'LEND',
                      'REN', 'LRC', 'BAL', 'WRX', 'SXP', 'YFI', 'STPT']
        self.pairs = ['BTC_DASH', 'BTC_DOGE', 'BTC_LTC', 'BTC_XEM', 'BTC_XRP', \
                      'USDT_BTC', 'USDT_DASH', 'USDT_LTC', 'USDT_XRP', 'BTC_ETH', 'USDT_ETH', \
                      'BTC_SC', 'BTC_DCR', 'BTC_LSK', 'BTC_STEEM', 'BTC_ETC', 'ETH_ETC', \
                      'USDT_ETC', 'BTC_REP', 'USDT_REP', 'BTC_ARDR', 'BTC_ZEC', 'ETH_ZEC', \
                      'USDT_ZEC', 'BTC_STRAT', 'BTC_GNT', 'BTC_ZRX', 'ETH_ZRX', 'BTC_CVC', \
                      'BTC_OMG', 'BTC_STORJ', 'BTC_EOS', 'ETH_EOS', 'USDT_EOS', 'BTC_SNT', \
                      'BTC_KNC', 'BTC_BAT', 'ETH_BAT', 'USDT_BAT', 'BTC_LOOM', 'USDT_DOGE', \
                      'USDT_GNT', 'USDT_LSK', 'USDT_SC', 'USDT_ZRX', 'BTC_QTUM', 'USDT_QTUM', \
                      'USDC_BTC', 'USDC_ETH', 'USDC_USDT', 'BTC_MANA', 'USDT_MANA', 'BTC_BNT', \
                      'USDC_XRP', 'USDC_DOGE', 'USDC_LTC', 'USDC_ZEC', 'BTC_POLY', 'BTC_ATOM', \
                      'USDC_ATOM', 'USDT_ATOM', 'USDC_DASH', 'USDC_EOS', 'USDC_ETC', \
                      'BTC_TRX', 'USDC_TRX', 'USDT_TRX', 'TRX_ETH', 'TRX_XRP', 'USDT_BTT', 'TRX_BTT', \
                      'USDT_WIN', 'TRX_WIN', 'TRX_STEEM', 'BTC_LINK', 'TRX_LINK', 'BTC_XTZ', \
                      'USDT_XTZ', 'TRX_XTZ', 'PAX_BTC', 'PAX_ETH', 'USDT_PAX', 'BTC_SNX', 'USDT_SNX',
                      'TRX_SNX', 'BTC_MATIC', 'USDT_MATIC', 'TRX_MATIC', 'BTC_MKR', \
                      'USDT_MKR', 'DAI_BTC', 'DAI_ETH', 'USDT_DAI', 'BTC_NEO', 'USDT_NEO', \
                      'TRX_NEO', 'BTC_AVA', 'USDT_LINK', 'USDT_AVA', 'TRX_AVA', 'BTC_CHR', \
                      'USDT_CHR', 'TRX_CHR', 'BNB_BTC', 'USDT_BNB', 'USDT_BUSD', 'TRX_BNB', 'BUSD_BNB', \
                      'BUSD_BTC', 'BTC_MDT', 'USDT_MDT', 'TRX_MDT', 'USDT_COMP', \
                      'ETH_COMP', 'BTC_LEND', 'USDT_LEND', 'BTC_REN', 'USDT_REN', \
                      'BTC_LRC', 'USDT_STEEM', 'USDT_LRC', 'USDT_BAL', 'ETH_BAL', \
                      'BTC_WRX', 'USDT_WRX', 'TRX_WRX', 'BTC_SXP', 'USDT_SXP', \
                      'TRX_SXP', 'USDT_YFI', 'BTC_STPT', 'USDT_STPT', 'TRX_STPT']
'''

