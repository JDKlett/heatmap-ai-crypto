#!/usr/bin/python

from tick import Tick
from batch import WindowProcessor

import json
import numpy as np
import sys 
import time
import requests

if len(sys.argv) != 7:
    print("Usage ./process.py <price_bands> <ticks_per_batch> <tolerance> <model> <pair> <delay>")
    print("e.g ./process.py 20 30 0.0015 ../processing/keras_bnb_50_epochs_7d.model/ BTCUSDT 30")
    exit(0)

from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import Normalizer


step_size=int(sys.argv[1])
batch_size=int(sys.argv[2])
tolerance=float(sys.argv[3])
model = keras.models.load_model(sys.argv[4])
pair = sys.argv[5]
delay = int(sys.argv[6])
#Eventually load samples from file
#samples = np.load(sys.argv[6])['arr_0']

url = 'https://api1.binance.com/api/v3/depth?symbol='+pair+'&limit=100'


def loadData():
    processor = WindowProcessor(batch_size,step_size,tolerance,delay)
    count = 0
    last_prediction = ""
    
    
    #scaler = MinMaxScaler()
    scaler = Normalizer()
    #scaler.fit(samples)
    
    while True:
        r = requests.get(url)
        try:
            data = r.json()
        except:
            print("Couldnt get data.")
            continue

        tick = Tick(data)
        processor.addTick(tick)
        sample = processor.getCurrentBatchSample();
        
        if sample == None:
            continue

        sample_data = sample['data']
        if len(sample_data) > 0  :
        # scaling
            array = np.array([sample_data])
            scaler.fit(array)
            normalized = scaler.transform(array)
        # attempt classification
            result = model.predict([normalized])
            labels = ['DOWN','SAME','UP']
            index = np.argmax(result)
            prediction = labels[index]
            processor.updateSamplePrediction(sample['id'], prediction, result)

    return processor


processor = loadData()

exit(0)

