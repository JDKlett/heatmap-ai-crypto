import numpy as np
import math

from sklearn import svm
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler


class Learn:
    def __init__(self, ratio, data):

        #scaling
        scaler = MinMaxScaler()
        samples = data['samples']
        scaler.fit(samples)
        self.samples = scaler.transform(samples)
        
        #encoding
        label_encoder = LabelEncoder()
        integer_encoded = label_encoder.fit_transform(np.array(data['labels']))
        # binary encode
        onehot_encoder = OneHotEncoder(sparse=False)
        integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
        onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
        self.labels = onehot_encoded
        
        
        num_samples = len(self.samples)
        print(num_samples)
        
        training_set_size = int(math.floor(ratio*num_samples))
        test_set_size = num_samples-training_set_size

        x_train = np.array(self.samples[:training_set_size])
        y_train = np.array(self.labels[:training_set_size])

        x_test = np.array(self.samples[training_set_size:])
        y_test = np.array(self.labels[training_set_size:])

     
        
        #try:
        model = Sequential()

        input_size = 1000
        output_size = int(len(y_train[0]))

        model.add(Dense(units=input_size, activation='relu'))
        model.add(Dense(units=input_size, activation='relu'))
        model.add(Dense(units=output_size, activation='softmax'))

        model.compile(loss='categorical_crossentropy',
                      optimizer='sgd',
                      metrics=['accuracy'])

        model.fit(x_train, y_train, epochs=200, batch_size=128)
        model.save("keras.model")
        loss_and_metrics = model.evaluate(x_test, y_test, batch_size=1)
        print(loss_and_metrics)

        #except ValueError:
        #    print("Classes: "+str(self.labels))
        #    print("Improper dataset, try different parameters.")

    def compareResults(self, expected, predicted):
        count = 0;
        ok = 0;
        total = len(expected)
        print("")
        print("-----------------")
        for count in range(total):
            print("|  "+expected[count] +"\t"+predicted[count]+"\t|")
            if expected[count] == predicted[count]:
                ok+=1
        print("-----------------")
        print("")
        print("Correct ratio: "+str(ok/total))

 

