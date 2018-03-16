import os
import csv
import ast
from collections import Counter
import numpy as np
import pandas
import matplotlib.pyplot as plt




if __name__ == '__main__':
    path = './data/'

    for i in range(1):  #Currenly a single loop only
        folderpath = './data/2'   #Check only games with 2 players
        data = []
        for csvname in os.listdir(folderpath):
            print("Filename:",csvname)
            with open(folderpath+"/"+csvname,'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    x = ast.literal_eval(row[2])

                    data.append((row[0],int(row[1]),x))
        n = len(data)
        endedGames = 0
        tileData = []
        for d in data:
            if d[0] != '':
                endedGames+=1
            for tile in d[2]:
                tileData.append((tile,d[1]))
        #Frequency and Barchart
        counter_data = Counter(list(zip(*tileData))[0])
        plt.bar(range(len(counter_data)), counter_data.values(), align='center')
        plt.xticks(range(len(counter_data)), counter_data.keys(),rotation='vertical')
        plt.show()
