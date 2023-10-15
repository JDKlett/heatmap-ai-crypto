#!/usr/bin/python

from tick import Tick
from batch import BatchProcessor

import json
import numpy as np
import os
import math
import sys 
import time



if len(sys.argv) != 8 and len (sys.argv) != 5:
    print("Usage ./process.py <price_bands> <ticks_per_batch> <tolerance> <raw_data_dir> <raw_data_files_to_load> <model_directory> <train/test_ratio>")
    print(" or   ./process.py <samples_to_load> <labels_to_load> <model_directory> <train/test_ratio>")
    print("e.g ./process.py 20 30 0.001 data300s 1000 models/keras_btc_015 0.85")
    print("e.g ./process.py samples.npz labels.npz models/keras_btc_015 0.85")
    exit(0)

from tflearn import Learn

if len(sys.argv) == 5:
    samples = np.load(sys.argv[1])['arr_0']
    labels = np.load(sys.argv[2])['arr_0']
    Learn(float(sys.argv[4]), sys.argv[3], {'samples': samples, 'labels':labels})
    exit(0)


step_size=int(sys.argv[1])
batch_size=int(sys.argv[2])
tolerance=float(sys.argv[3])
directory=sys.argv[4]
number_files=int(sys.argv[5])
model_dir = sys.argv[6]
ratio=float(sys.argv[7])


filename='data'
prices=[]
try:
    os.makedirs("last_execution")
except:
    print("Last execution dir created")
    #do nothing


def loadData():
    processor = BatchProcessor(batch_size,step_size,tolerance)
    start_time = time.time()
    for count in range(number_files):
        sys.stdout.flush()
        sys.stdout.write("\rProcessing ticks ("+str(round((count+1)*100/number_files))+"%)")
        with open(directory+'/'+filename+str(count)+".json") as json_file:
            try:
                data = json.load(json_file)
                tick = Tick(data)
                processor.addTick(tick)
                json_file.close()
            except:
               print("Cannot load data.")
    end_time = time.time()
    print("\nProcessing took "+str(round(end_time-start_time))+"s");
    return processor


processor = loadData()
samples = processor.getSampleList()

#Learn(ratio, model_dir, samples)

exit(0)

