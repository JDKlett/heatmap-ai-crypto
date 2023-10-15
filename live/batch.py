import numpy as np
import math
import json
import sys

class Window:
    def __init__(self, price_bands, tolerance, batch_size):
        self.counter = 0
        self.price_bands = price_bands
        self.tolerance = tolerance
        self.ticks = []
        self.samples = {}
        self.verifiable_samples = []
        self.batch_size = batch_size;
        self.window_size = batch_size+2;
        self.max_history = batch_size+2;
        self.current_sample_id = 0;
        self.current_sample = None

    def addTick(self, tick):
        self.ticks.append(tick)
        self.update()

    def update(self):
       
        if len(self.ticks) < self.window_size:
            sys.stdout.flush()
            sys.stdout.write("\rNot enough samples: ("+str(len(self.ticks))+"/"+str(self.window_size)+")")
            return -1

        if len(self.ticks) > self.window_size:
            while len(self.ticks) > self.window_size:
                self.ticks.pop(0)
        
        
        old_ticks_subset = self.ticks[:self.batch_size]
        current_ticks_subset = self.ticks[self.window_size-self.batch_size:]
        
        label = "SAME"
        
        max_price_ask = 0;
        max_price_bid = 0;
        min_price_ask = float("inf")
        min_price_bid = float("inf")

        for tick in current_ticks_subset:
            max_price_ask = max(max_price_ask,tick.getMaxAskPrice());
            max_price_bid = max(max_price_bid,tick.getMaxBidPrice());
            min_price_ask = min(min_price_ask,tick.getMinAskPrice());
            min_price_bid = min(min_price_bid,tick.getMinBidPrice());
 
        price_step = round((max_price_ask - min_price_bid)/self.price_bands,10);

        price = old_ticks_subset[-1].getMarketPrice()
        price_low = price-price*self.tolerance
        price_high = price+price*self.tolerance
        sample = [] 
        for tick in current_ticks_subset:
            asks = tick.getAsks()
            bids = tick.getBids()
            sample_row_asks = np.zeros(self.price_bands)
            sample_row_bids = np.zeros(self.price_bands)
            if (label == "SAME") and (float(tick.getMarketPrice()) > price_high):
                label = "UP"
            elif (label == "SAME") and (float(tick.getMarketPrice()) < price_low):
                label = "DOWN"

            for ask in asks:
                price = ask[0]
                size = ask[1]
                index = math.floor((ask[0] - min_price_bid)/price_step)
                if index >= self.price_bands:
                    index = (self.price_bands-1)
                sample_row_asks[index]+=size*price
            for bid in bids:
                price = bid[0]
                size = bid[1]
                index = math.floor((bid[0] - min_price_bid)/price_step)
                if index >= self.price_bands:
                    index = (self.price_bands-1)
                sample_row_bids[index]+=size*price

            sample = np.concatenate((sample,sample_row_asks))
            sample = np.concatenate((sample,sample_row_bids))
        self.current_sample = {'data':sample,'id':self.current_sample_id}

        self.samples[self.current_sample_id] = self.current_sample
        
        verifiable_sample_index = (self.current_sample_id - self.batch_size + self.max_history) % self.max_history
        if verifiable_sample_index in self.samples:
            self.samples[verifiable_sample_index]['label'] = label    
            self.verifiable_samples.append(self.samples[verifiable_sample_index])
        self.current_sample_id = (self.current_sample_id+1) % self.max_history
        return self.current_sample_id

    def getSample(self, sample_id):
        return self.samples[sample_id]

    def getVerifiableSample(self):
        if( len(self.verifiable_samples) > 0):
            return self.verifiable_samples.pop(0)
        else:
            return None

    def getLastSample(self):
        return self.current_sample

class WindowProcessor:
    def __init__(self, batch_size, price_bands, tolerance, delay):
        self.counter = 0
        self.price_bands = price_bands
        self.batch_size = batch_size
        self.predictions = {}
        self.window = Window(price_bands, tolerance, batch_size)
        self.tolerance = tolerance
        self.total_counter = 1
        self.total_correct = 1
        self.total_no_same_correct = 1
        self.total_no_same_counter = 1
        self.delay = 0
        self.max_delay = delay

    def updateSamplePrediction(self, sample_id, prediction, result):
        to_update = self.window.getSample(sample_id)
        to_update['prediction'] = prediction
        to_update['result'] = result
        if self.delay % self.max_delay == 0:
            self.verifySamplePrediction()
        self.delay = self.delay +1

    def addTick(self, tick):
        self.window.addTick(tick)
        
    def getCurrentBatchSample(self):
        return self.window.getLastSample()

    def verifySamplePrediction(self):

        to_verify = self.window.getVerifiableSample()
        if to_verify != None and 'label' in to_verify:
            if to_verify['label'] == to_verify['prediction']:
                self.total_correct+=1
            self.total_counter+=1
            if to_verify['prediction'] != 'SAME':
                if to_verify['label'] == to_verify['prediction']:
                    self.total_no_same_correct+=1
                self.total_no_same_counter+=1
            print("Predicted: " + to_verify['prediction'] + " Real: "+to_verify['label'])
            print("Results: "+ str(to_verify['result']))
            print("Samples:"+str(self.total_counter)+" Rate:"+str(float(self.total_correct/self.total_counter)))
            print("No same Samples:"+str(self.total_no_same_counter)+" Rate:"+str(float(self.total_no_same_correct/self.total_no_same_counter)))
        else:
           print("Sample result not yet calculated.")

