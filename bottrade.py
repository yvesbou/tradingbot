

class BotTrade(object):
    def __init__(self, currentPrice, balance_coin1, balance_coin2, log):
        self.output = log
        self.entryPrice = currentPrice
        self.balance_coin1 = balance_coin1
        self.balance_coin2 = balance_coin2
        self.balance_coin2 = self.balance_coin1 / self.entryPrice
        self.balance_coin1 = 0
        self.fee = 0.125  # in percent

    def balance_check(self):
        return self.balance_coin1, self.balance_coin2
