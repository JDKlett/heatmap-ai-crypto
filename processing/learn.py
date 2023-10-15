import numpy as np
import math

from sklearn import svm

class Learn:
    def __init__(self, ratio, samples):
        self.labels = samples['labels']
        self.samples = samples['samples']

        num_samples = len(self.samples)
        training_set_size = int(math.floor(ratio*num_samples))
        test_set_size = num_samples-training_set_size

        training_set = self.samples[:training_set_size]
        training_set_labels = self.labels[:training_set_size]

        test_set = self.samples[training_set_size:]
        test_set_labels = self.labels[training_set_size:]


        try:
            clf = svm.SVC()
            clf = svm.SVC(decision_function_shape='ovo')
            clf.fit(training_set,training_set_labels)
            result = clf.predict(test_set)
            self.compareResults(test_set_labels,result)
        except ValueError:
            print("Classes: "+self.labels)
            print("Improper dataset, try different parameters.")

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

 

