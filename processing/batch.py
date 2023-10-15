import numpy as np
import math
import json

class Batch:
    def __init__(self, id, price_bands):
        self.id = id
        self.price_bands = price_bands
        self.ticks = []
        self.max_price_ask = 0;
        self.max_price_bid = 0;
        self.min_price_ask = float("inf")
        self.min_price_bid = float("inf")
        self.sample = []
        self.label = "SAME"

    def getLabel(self):
        return self.label

    def addTick(self, tick):
        self.max_price_ask = max(self.max_price_ask,tick.getMaxAskPrice());
        self.max_price_bid = max(self.max_price_bid,tick.getMaxBidPrice());
        self.min_price_ask = min(self.min_price_ask,tick.getMinAskPrice());
        self.min_price_bid = min(self.min_price_bid,tick.getMinBidPrice());
        self.ticks.append(tick)

    def close(self, price, tolerance):

        price_step = round((self.max_price_ask - self.min_price_bid)/self.price_bands,10);

        price_low = price-price*tolerance
        price_high = price+price*tolerance

        for tick in self.ticks:
            asks = tick.getAsks()
            bids = tick.getBids()
            sample_row_asks = np.zeros(self.price_bands)
            sample_row_bids = np.zeros(self.price_bands)
            if (self.label == "SAME") and (float(tick.getMarketPrice()) > price_high):
                self.label = "UP"
            elif (self.label == "SAME") and (float(tick.getMarketPrice()) < price_low):
                self.label = "DOWN"

            for ask in asks:
                price = ask[0]
                size = ask[1]
                index = math.floor((ask[0] - self.min_price_bid)/price_step)
                if index >= self.price_bands:
                    index = (self.price_bands-1)
                sample_row_asks[index]+=size*price
            for bid in bids:
                price = bid[0]
                size = bid[1]
                index = math.floor((bid[0] - self.min_price_bid)/price_step)
                if index >= self.price_bands:
                    index = (self.price_bands-1)
                sample_row_bids[index]+=size*price

            self.sample = np.concatenate((self.sample,sample_row_asks))
            self.sample = np.concatenate((self.sample,sample_row_bids))
            self.last_price = tick.getMarketPrice()

    def getSample(self):
        return self.sample

    def getFirstPrice(self):
        return self.ticks[0].getMarketPrice()
    
    def getLastPrice(self):
        return self.last_price

    def getSize(self):
        return len(self.ticks)

class BatchProcessor:
    def __init__(self, batch_size, price_bands, tolerance):
        self.counter = 0
        self.price_bands = price_bands
        self.batch_size = batch_size
        self.batch_list = [Batch(0, price_bands)]
        self.tolerance = tolerance

    def addTick(self, tick):
        current_batch = self.batch_list[-1]
        if(current_batch.getSize() < self.batch_size):
            current_batch.addTick(tick)
        else:
            previous_batch = None
            if len(self.batch_list) > 2:
                previous_batch = self.batch_list[-2]
            if previous_batch != None:
                last_price = previous_batch.getLastPrice()  
            else:
                last_price = current_batch.getFirstPrice()
            current_batch.close(last_price,self.tolerance)
            self.counter += 1
            self.batch_list.append(Batch(self.counter,self.price_bands))

    
    def getSampleList(self):
        sample_list =[];
        labels = [];
        for batch in self.batch_list:
            if len(batch.getSample()) == (self.price_bands*self.batch_size*2):
                sample_list.append(batch.getSample())
                labels.append(batch.getLabel())
        data = {'samples':sample_list, 'labels':labels}
        np.savez('last_execution/samples', sample_list)
        np.savez('last_execution/labels', labels)
        return data
