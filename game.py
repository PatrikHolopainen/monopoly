import random
import itertools
from tile import *
from player import *


class Game():
    def __init__(self,n_players):
        self.tiles = [
        Empty("Start",200),
        Street("Brown1",60,[2,10,30,90,160,250],"brown",50),
        Card("CommunityChest1","chest"),
        Street("Brown2",60,[4,20,60,180,320,450],"brown",50),
        Tax("Income",-200),
        Railroad("Railroad1",200,25),
        Street("Blue1",100,[6,30,90,270,400,550],"blue",50),
        Card("Choice1","choice"),
        Street("Blue2",100,[6,30,90,270,400,550],"blue",50),
        Street("Blue3",120,[8,40,100,300,450,600],"blue",50),
        Empty("Jail",0),
        Street("Pink1",140,[10,50,150,450,625,750],"pink",100),
        Utility("Utility1",150,4),
        Street("Pink2",140,[10,50,150,450,625,750],"pink",100),
        Street("Pink3",160,[12,6,180,500,700,900],"pink",100),
        Railroad("Railroad2",200,25),
        Street("Orange1",180,[14,70,200,550,750,950],"orange",100),
        Card("CommunityChest2","chest"),
        Street("Orange2",180,[14,70,200,550,750,950],"orange",100),
        Street("Orange3",200,[16,80,220,600,800,1000],"orange",100),
        Empty("Free",0),
        Street("Red1",220,[18,90,250,700,875,1050],"red",150),
        Card("Choice2","choice"),
        Street("Red2",220,[18,90,250,700,875,1050],"red",150),
        Street("Red3",240,[20,100,300,750,925,1100],"red",150),
        Railroad("Railroad3",200,25),
        Street("Yellow1",260,[22,110,330,800,975,1150],"yellow",150),
        Street("Yellow2",260,[22,110,330,800,975,1150],"yellow",150),
        Utility("Utility2",150,4),
        Street("Yellow3",280,[24,120,360,850,1025,1200],"yellow",150),
        GoToJail("GoToJail"),
        Street("Green1",300,[26,130,390,900,1100,1275],"green",200),
        Street("Green2",300,[26,130,390,900,1100,1275],"green",200),
        Card("CommunityChest3","chest"),
        Street("Green3",320,[28,150,450,1000,1200,1400],"green",200),
        Railroad("Railroad4",200,25),
        Card("Choice3","choice"),
        Street("DBlue1",350,[35,175,500,1100,1300,1500],"dblue",200),
        Tax("Luxury",-100),
        Street("DBlue2",400,[50,200,600,1400,1700,2000],"dblue",200),
        ]
        self.players = []
        for i in range(n_players):
            self.players.append(Player(str(i+1),1500,self))
        self.seed = random.randrange(len(self.players))
        self.turn = 0
        self.winner = None

        z = len(self.tiles) #Link tiles together
        for i in range(z):
            self.tiles[i].prev = self.tiles[(i-1)%z]
            self.tiles[i].next = self.tiles[(i+1)%z]
        for x in self.players: #Set starting Tile
            x.tile = self.tiles[0]

    def oneTurn(self):
        result = self.currentPlayer().turn()

        if type(result) != bool:
            print("Type error")
            return False

        if not result:
            #print(self.currentPlayer().name + "LOST THE GAME")
            self.removePlayer(self.currentPlayer())
        if len(self.players) > 1:
            self.turn+=1
            return True
        else:
            self.winner = self.players[0]
            return False

    def currentPlayer(self):
        return self.players[(self.turn+self.seed)%len(self.players)]

    def removePlayer(self,player):
        for t in player.ownedTiles():
            t.reset()
        self.players.remove(player)
        #print("removePlayer: removed ",player.name,"\nremaining players:",self.players)

    def getStats(self):
        s = []
        for x in self.players:
            s.append(x.name)
            s.append(x.money)
            s.append(len(x.ownMortgaged()))
            s.append(len(x.ownedTiles()))
            #s.append(  (len (x.ownedTiles()) ,"/", len(x.ownMortgaged())  )  )
        return s
