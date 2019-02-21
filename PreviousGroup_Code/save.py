import visa
from matplotlib import pyplot as plt
from time import time
import csv


# Writes all the data to a csv with two columns (time/output)
# loc corresponds to the extension in active folder, including name of file
# x, t are variables used for output, time
def writetocsv(x,t,loc,counter):
    with open(loc+'\data_' + str(counter) + '.csv', mode='w') as csv_file:
        # Specify headers
        fieldnames = ['time', 'output']

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
        writer.writeheader()
        # Write rows of data
        for i in range(len(x)):
            writer.writerow({'time': str(t[i]), 'output': str(x[i])})

