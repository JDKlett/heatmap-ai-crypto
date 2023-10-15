import numpy as np

class Tick:
    def __init__(self, data):
        self.best_bid = float(data['bids'][0][0])
        self.best_ask = float(data['bids'][0][0])
        self.market_price = (self.best_ask+self.best_bid)/2 
        self.bids = np.array(data['bids']).astype(np.float)
        self.asks = np.array(data['asks']).astype(np.float)
        self.orderbook = np.concatenate((self.bids,self.asks))
        self.id = data['lastUpdateId']

    def getBids(self):
        return self.bids
    
    def getAsks(self):
        return self.asks

    def getMinBidPrice(self):
        return np.min(self.bids,axis=0)[0]

    def getMaxBidPrice(self):
        return np.max(self.bids,axis=0)[0]

    def getMinAskPrice(self):
        return np.min(self.asks,axis=0)[0]

    def getMaxAskPrice(self):
        return np.max(self.asks,axis=0)[0]


    def getOrderbook(self):
        return self.orderbook

    def getMarketPrice(self):
        return self.market_price;
