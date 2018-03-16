import random
from collections import Counter
from game import *
import csv
import time
import os.path


def runGame(n_players,n,cap):
    data = []
    for i in range(n):
        winningTiles = []
        game = Game(n_players)
        turnCounter = 0
        stats = []
        while(game.oneTurn() and  turnCounter < cap):
            #print("TURN:",turnCounter)
            turnCounter +=1
            stats.append(game.getStats())

        print("Game:",i,turnCounter,"Winner:",game.winner)
        if game.winner:
            for t in game.winner.ownedTiles():
                winningTiles.append(t.name)
        data.append((game.winner,turnCounter,winningTiles))

    #print(data)
    return data
    #return Counter(winningTiles)

if __name__ == '__main__':

    for i in range(2,3):
        a,b,c = i,1000,1000 #player_amount,game_amount,max_total_turns
        data = runGame(a,b,c)

        moment=time.strftime("%Y-%b-%d__%H-%M-%S",time.localtime())
        path = './data/'+str(a)
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path+'/'+moment+'.csv', 'w',newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(data)
    
