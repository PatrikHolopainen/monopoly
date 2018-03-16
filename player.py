import random
import itertools
from tile import *


class Player():
    def __init__(self,name,money,game):
        self.name = "Player" + name
        self.money = money
        self.tile = None
        self.inJail = 0
        self.freeJailCard = 0
        self.game = game

    def __repr__(self):
        return self.name

    def crazySuperAI(self): #TODO
        mp = self.mortgagePriority()
        z = 2 #Require atleast z*mortPrice money before openning a mortgage
        for i in range(len(mp)):
            if self.money > z*mp[i].mortPrice:
                mp[i].toggleMort()

        #buyhouse
        hp = self.housePriority()
        for i in range(len(hp)):
            while(hp[i].canDecreaseOrIncrease()[1] and self.money > 2*hp[i].housePrice and self.buyHouse(hp[i])):
                pass
                #print(self.name,"bought a house on",hp[i].name)

    def ownedTiles(self):
        current = self.tile.next
        boole = True
        ot = []
        while(boole):
            if isinstance(current,Property) and current.owner == self:
                ot.append(current)
            current = current.next
            if current == self.tile:
                boole = False
        return ot

    def mortgagePriority(self):
        ownMorts = [] #Get Own mortgaged tiles
        for t in self.ownedTiles():
            if t.mort:
                ownMorts.append(t)
        if len(ownMorts) > 0:
            ownMorts = sorted(ownMorts,key=lambda x: x.buyPrice)
        for t in ownMorts: #Move full-group properties to the end
            if type(t)== Street and t.hasFullGroup(False):
                ownMorts.remove(t)
                ownMorts.append(t)
        ownMorts.reverse()
        #print("OwnMorts:",ownMorts)
        return ownMorts

    def housePriority(self):
        temp = []
        for t in self.ownedTiles():
            if type(t)==Street and t.canDecreaseOrIncrease()[1]:
                temp.append(t)
        temp = sorted(temp,key=lambda t: t.buyPrice,reverse=True)

        return temp

    def buyHouse(self,tile):
        if tile.canDecreaseOrIncrease()[1] and self.money > tile.housePrice:
            return tile.setRentLevel(True)
        else:
            #print("BUYHOUSE FAILED ERROR ERROR\n\n\n\n\n\n\n\n")
            return False

    def payRepairs(self,perHouse,perHotel):
        amount = 0
        for t in self.ownedTiles():
            if type(t) == Street:
                if t.priceLevel == 5:
                    amount += perHotel
                else:
                    amount += t.priceLevel*perHouse
        #print(self.name,"has to pay ",amount)
        return self.bankTransaction(amount)

    def collectFromOthers(self,amount): #TODO
        #print("Collect!")

        for x in self.game.players:
            if x != self:
                if not x.pay(self,amount):
                    return False
        return True

    def moveToNearest(self,place):
        if place == 'uti':
            return self.move(0,False,["Utility1","Utility2"])
        elif place == 'rr':
            return self.move(0,False,["Railroad1","Railroad2","Railroad3","Railroad4"])
        else:
            #print("Wrong place",place)
            return False


    def wantsOut(self):
        return True #TODO

    def getOutOfJailCard(self):
        self.freeJailCard+=1
        return True

    def rollDice(self):
        return(random.randrange(1,7),random.randrange(1,7))

    def goToJail(self):
        #print(self.name, "is going to JAIL")
        self.inJail = 3
        return(self.move(0,False,'Jail'))

    def move(self,n,startMoney,target):
        if target:
            while self.tile.name not in target:
                #print(self.tile.name)
                if startMoney:
                    self.tile = self.tile.next
                    if self.tile.name == "Start":
                        self.bankTransaction(self.tile.amount)
                else:
                    self.tile = self.tile.prev
            return True

        else:
            if n > 0:
                for i in range(n):
                    self.tile = self.tile.next
                    if self.tile.name == "Start":
                        self.bankTransaction(self.tile.amount)
            elif n < 0:
                for i in range(abs(n)):
                    self.tile = self.tile.prev
        #print(self.name,"to",self.tile.name)
        a = self.tile.action(self,n)
        #print("a is",a )
        return(a)

    def normalRoll(self):
        dice = self.rollDice()
        n =dice[0]+dice[1]
        #CheckDoubles
        doubles = False
        doubleCount = 0
        okay = True
        while(okay and doubleCount == 0 or doubles):
            #print(self.name,"is in",self.tile.name,"and threw",dice)
            if(doubleCount == 3):
                #print("okaygotojail")
                okay = self.goToJail()
            else:
                #print("okaymove")
                okay = self.move(n,True,None)
                #print("okay is ",okay)
                #print(self.name,self.tile.name,self.money,self.inJail)
                doubles = dice[0]==dice[1]
                dice = self.rollDice()
            doubleCount +=1
        #print("returning okay")
        return okay

    def turn(self):

        self.crazySuperAI()

        if self.inJail > 0:
            if self.freeJailCard > 0:
                self.inJail = 0
                self.freeJailCard -= 1
                #print("Used the free jail Card")

                return self.turn()
            dice = self.rollDice()
            #print(self.name,"is in jail",self.inJail)
            doubles = dice[0]==dice[1]
            n = dice[0]+dice[1]
            if(doubles):
                self.inJail = 0

                return(self.move(n,True,None))
            elif self.inJail == 1:
                self.inJail = 0
                if(self.bankTransaction(-50)):

                    return(self.move(n,True,None))
                else:

                    return False
            else:
                self.inJail -=1

                return True
        else:
            t = self.normalRoll()
            #print("t is",t)
            return t

    def bankTransaction(self,amount):
        #print("Bank transaction start",self.money,amount)
        if amount < 0 and self.money < abs(amount):
            #print("a")
            #print(self.name,"did not have",abs(amount),"to pay the bank")
            if self.needMoney(abs(amount)-self.money):
                self.money += amount
                #print("b")
                #print("Bank transaction end",self.money,amount)
                return True
            else:
                #print("c")
                #print("Bank transaction end",self.money,amount)
                return False
        else:
            self.money += amount
            #print(self.name,"dealt with bank:",amount)
            #print("d")
            #print("Bank transaction end",self.money,amount)
            return True

    def pay(self,receiver,amount):
        #print(self.name,self.money,"pays",amount,"to",receiver.name,receiver.money)
        if self.money < amount:
            #print (self.name,"did not have",amount,"to pay to",receiver.name)
            if self.needMoney(amount-self.money):
                receiver.money += amount
                self.money -= amount
                return True
            else:
                return False
        else:
            receiver.money += amount
            self.money -= amount
            #print(self.name,"just paid",amount,"to",receiver.name)
            return True

    """
        method needMoney
        categorize own property into 3 types:
        1) instantly mortgageable
        2) full groups of streets without houses (double rent)
        3) streets with houses
        Within these categories rank the properties based
        on their buyPrice. Go through the categories in ascending order,
        and move only to the next one if the total sum of properties
        being mortgaged/houses sold is not enough. Get the required
        properties and then optimise the mortgaging of those properties.
    """
    def ownMortgaged(self):
        oms = []
        for t in self.ownedTiles():
            if t.mort:
                oms.append(t)
        return oms

    def needMoney(self,amount):
        #print("SOS",self.name, "needs",amount)
        #print("His tiles:")
        #for z in self.ownedTiles():
            #print(z.name,z.mort)
        freeToMort = [] #Get indexes of not mortgaged properties
        housed = []
        grouped = []
        for i in range(len(self.ownedTiles())): #TODO Bug
            if not self.ownedTiles()[i].mort:
                if type(self.ownedTiles()[i])==Street and self.ownedTiles()[i].hasFullGroup(True)and self.ownedTiles()[i].groupHasHouses():
                    housed.append(i)
                elif type(self.ownedTiles()[i])==Street and self.ownedTiles()[i].hasFullGroup(True):
                    grouped.append(i)
                else:
                    freeToMort.append(i)

        # print("NeedMoneyTest:")
        # for i in freeToMort:
        #     print("F2M:",self.ownedTiles()[i].name)
        # for i in grouped:
        #     print("F2M:",self.ownedTiles()[i].name)
        # for i in housed:
        #     print("HS:",self.ownedTiles()[i].name,self.ownedTiles()[i].priceLevel)
        mortValues = []
        for i in freeToMort:
            mortValues.append(self.ownedTiles()[i].mortPrice)
        n_mort = len(freeToMort)
        n_group = len(grouped)
        n_house = len(housed)

        usableTiles = list(zip(freeToMort,mortValues))
        difference = amount
        if n_mort > 0:
            difference = amount- sum(mortValues)
            usableTiles = sorted(usableTiles,key=lambda x: x[1])

        if n_mort > 0 and difference > 0: #We need at least grouped tiles
            groupedValues = []
            for i in grouped:
                groupedValues.append(self.ownedTiles()[i].mortPrice)
            groupTuples = list(zip(grouped,groupedValues))
            groupTuples = sorted(groupTuples,key=lambda x: x[1])

            for i in range(len(groupTuples)):
                if difference > 0:
                    #print("added",groupTuples[i],"to mortgageable tiles")
                    usableTiles.append(groupTuples[i])
                    difference -= groupTuples[i][1]

            if n_house > 0 and difference > 0:
                #print("Need houses, diff:",difference)
                housedValues = []
                for i in housed:
                    housedValues.append(self.ownedTiles()[i].mortPrice)
                houseTuples = list(zip(housed,housedValues))
                houseTuples = sorted(houseTuples,key=lambda x: x[1])
                count = len(houseTuples)
                maxRuns= 0
                for i,j in houseTuples:
                    maxRuns += (1+self.ownedTiles()[i].priceLevel)
                run = 0
                while(difference > 0 and run < maxRuns):
                    i = 0
                    notDone = True
                    while(notDone and i < len(houseTuples)):
                        temp = self.ownedTiles()[houseTuples[i][0]]
                        if  temp not in usableTiles and temp.priceLevel == 0 and not temp.groupHasHouses():
                            usableTiles.append(houseTuples[i])
                            difference -= temp.mortPrice
                            notDone = False
                        elif temp not in usableTiles and temp.canDecreaseOrIncrease()[0]:
                            if temp.setRentLevel(False):
                                #print("Sold a house on",temp.name,"for",temp.housePrice/2)
                                difference -= temp.housePrice/2
                                notDone = False
                        else:
                            i+=1
                    run+=1

        return(self.optimisedMortgaging(usableTiles,amount))

    """
        method optimisedMortgaging

        Method needMoney takes care of selecting to properties
        to be sold, and optimiseMortgaging mortgages them based on
        2 factors:
         1) Least property needed to be mortgaged
         2) Lowest total sum to be mortgaged
        This is done by going through the combinations (itertools.combinations)
        of all the mortgageable properties.
        Returns true if c amount of money can be gained by morts,
        otherwise returns False
    """

    def optimisedMortgaging(self,tup,c):
        if c > 4000:
            #print("C was too big:",c)
            return False
        #print("Started optimising to get",c,"with",tup)
        n = len(tup)
        for i in range(1,n+1):
            combs = list(itertools.combinations(tup,i))
            for j in range(len(combs)):
                currentValue = 0
                for x in combs[j]:
                    currentValue+=x[1]
                if currentValue >= c:
                    for x in combs[j]:
                        self.ownedTiles()[x[0]].toggleMort()
                    #print("Yeeah optimised succesfull")
                    return True

        #print("Optimisation is not enough")
        return False

    def wantsToBuy(self):
        return True
    def description(self):
        return self.name,self.money,self.tile.name

    def __str__(self):
        return self.name