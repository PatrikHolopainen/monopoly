import random
import itertools


class Tile():
    def __init__(self,name):
        self.name = name
        self.prev = None
        self.next = next

    def action(self,player,n):
        raise NotImplementedError

class Special(Tile):
    def __init__(self,name):
        Tile.__init__(self,name)

class Empty(Special):
    def __init__(self,name,amount):
        Special.__init__(self,name)
        self.amount = amount

    def action(self,player,n):
        #print("ACTION:",player.name,"TO", self.name, "WITH", n)
        #print("Nothing happens, bruv")
        return True

class Card(Special): #TODO CARD FUNCTIOANLITY
    choindex = 0
    cheindex = 0

    chocards = [("Advance to go",lambda pl:pl.move(0,True,'Start,')),
    ("Advance to Red3",lambda pl:pl.move(0,True,'Red3,')),
    ("Advance to Pink1",lambda pl:pl.move(0,True,'Pink1,')),
    ("Go to nearest Utility",lambda pl:pl.moveToNearest('uti')),
    ("Go to nearest Railroad",lambda pl:pl.moveToNearest('rr')),
    ("Go to nearest Railroad",lambda pl:pl.moveToNearest('rr')),
    ("Bank pays you dividend +50",lambda pl:pl.bankTransaction(50)),
    ("Get out of Jail",lambda pl:pl.getOutOfJailCard()),
    ("Go back 3 spaces",lambda pl:pl.move(-3,False,None)),
    ("Go to Jail",lambda pl:pl.goToJail()),
    ("Street repairs -25/-100",lambda pl:pl.payRepairs(25,100)),
    ("Pay poor tax -15",lambda pl:pl.bankTransaction(-15)),
    ("Advance to Railroad1",lambda pl:pl.move(0,True,'Railroad1')),
    ("Advance to DBlue2",lambda pl:pl.move(0,True,'DBlue2')),
    ("You have been elected chairman -50/plrs",lambda pl:pl.collectFromOthers(-50)),
    ("Your building loan matures +150",lambda pl:pl.bankTransaction(150)),
    ("You have won a crossword competition +100",lambda pl:pl.bankTransaction(100))
    ]
    checards = [
    ("Advance to go",lambda pl:pl.move(0,True,'Start')),
    ("Bank error in your favor +75",lambda pl:pl.bankTransaction(75)),
    ("Doctor's fees -50",lambda pl:pl.bankTransaction(-50)),
    ("Get out of Jail",lambda pl:pl.getOutOfJailCard()),
    ("Go to Jail",lambda pl:pl.goToJail()),
    ("Birthday, +10/plrs",lambda pl:pl.collectFromOthers(10)), #TODO
    ("Grand opera night, +50/plrs",lambda pl:pl.collectFromOthers(50)),
    ("Income tax refund +20",lambda pl:pl.bankTransaction(20)),
    ("Life insurance matures +100",lambda pl:pl.bankTransaction(100)),
    ("Pay hospital fees -100",lambda pl:pl.bankTransaction(-100)),
    ("Pay school fees -50",lambda pl:pl.bankTransaction(-50)),
    ("Receive consultancy fee -25",lambda pl:pl.bankTransaction(-25)),
    ("Street repairs -40/-115",lambda pl:pl.payRepairs(40,115)),
    ("Second prize in a beauty contest +10",lambda pl:pl.bankTransaction(10)),
    ("Inheritance +100",lambda pl:pl.bankTransaction(100)),
    ("Sale of stock +50",lambda pl:pl.bankTransaction(50)),
    ("Holiday fund matures +100",lambda pl:pl.bankTransaction(100))
    ]
    random.shuffle(chocards)
    random.shuffle(checards)


    def __init__(self,name,cardType):
        Special.__init__(self,name)
        self.cardType = cardType

    def action(self,player,n):
        card = None
        if(self.cardType == 'choice'):
            card = Card.chocards[Card.choindex%len(Card.chocards)]
            Card.choindex +=1
        else:
            card = Card.checards[Card.cheindex%len(Card.checards)]
            Card.cheindex +=1
        #print("CARD:",card[0])
        #print(card[0])

        return card[1](player)

class Tax(Special):
    def __init__(self,name,taxAmount):
        Special.__init__(self,name)
        self.taxAmount = taxAmount
    def action(self,player,n):
        #print("ACTION:",player.name,"TO", self.name, "WITH", n)
        return(player.bankTransaction(self.taxAmount))

class GoToJail(Special):
    def __init__(self,name):
        Special.__init__(self,name)

    def action(self,player,n):
        return(player.goToJail())

class Property(Tile):

    def __init__(self,name,buyPrice):
        Tile.__init__(self,name)
        self.owner = None
        self.mort = False
        self.buyPrice = buyPrice
        self.mortPrice = int(buyPrice/2)

    def getPrice(self,die): #Get the price of the property
        raise NotImplementedError

    def reset(self):
        self.owner = None
        self.mort = False

    def action(self,player,n):
        #print("Property ACTION:",player.name,"TO", self.name, "WITH", n)

        if self.owner == None: #Property purchase
            #print("Owner none")
            if player.wantsToBuy() and player.money > self.buyPrice:
                #print(player.name,"purchased",self.name,"with",self.buyPrice)
                player.money -= self.buyPrice
                #player.ownedTiles.append(self)
                self.owner = player
            #else:  #TODO Auction?
                #print(player.name,"did not buy",self.name,"(Cost/Available):",self.buyPrice,player.money)
            return True

        elif self.owner != player and not self.mort: #Pay rent only if not mortgaged
            #print(player.name,"landed on ",self.name,",owned by",self.owner.name)

            z = player.pay(self.owner,self.getPrice(n))
            #print("z is",z)
            return(z)

        elif self.owner == player or self.mort:
            #print(player.name,"landed on his own tile or was mort")
            return True

    def toggleMort(self):
        if not self.mort:
            #print(self.owner.name,"mortgaged",self.name,"for",self.mortPrice)
            self.mort = True
            return(self.owner.bankTransaction(self.mortPrice))
        else:
            #print(self.owner.name,"opened",self.name,"for",-1.1*self.mortPrice)
            self.mort = False
            return(self.owner.bankTransaction(int(-1.1*self.mortPrice)))

class Street(Property):
    def __init__(self,name,buyPrice,priceList,color,housePrice):
        Property.__init__(self,name,buyPrice)
        self.priceList = priceList
        self.color = color
        self.housePrice = housePrice
        self.priceLevel = 0

    def getGroup(self):
        colourCount = 0 #Owner owns whole group?
        nextTile = self.next
        group = [self]
        while(nextTile != self):
            if type(nextTile) == Street and nextTile.color == self.color:
                group.append(nextTile)
            nextTile = nextTile.next
        return group

    def reset(self):
        self.priceLevel = 0

    def canDecreaseOrIncrease(self):
        dec = False
        inc = False
        if all(x.priceLevel <= self.priceLevel for x in self.getGroup()) and self.priceLevel > 0:
            dec = True
        if all(x.priceLevel >= self.priceLevel for x in self.getGroup()) and self.priceLevel < 5:
            inc = True
        return (dec,inc)

    def setRentLevel(self,raiseRent):
        if self.hasFullGroup(True):
            if raiseRent and self.canDecreaseOrIncrease()[1]:
                self.priceLevel +=1
                return self.owner.bankTransaction(-self.housePrice)
            elif not raiseRent and self.canDecreaseOrIncrease()[0]:
                self.priceLevel -=1
                return self.owner.bankTransaction(self.housePrice/2)
        #print("setRentLevel failed for",self.name,"raiseRent:",raiseRent)
        return False

    def hasFullGroup(self,checkMort):
        if(checkMort):
            return all(x.owner == self.owner and not x.mort for x in self.getGroup())
        else:
            return all(x.owner == self.owner for x in self.getGroup())

    def groupHasHouses(self):
        return not all(x.priceLevel == 0 for x in self.getGroup())

    def getPrice(self,die):
        colourCount = 0 #Owner owns whole group?
        for tile in self.owner.ownedTiles():
            if type(tile) == Street and tile.color == self.color:
                colourCount+=1
        multiplier = 1
        if self.hasFullGroup(True) and self.priceLevel == 0: multiplier = 2
        return self.priceList[self.priceLevel]*multiplier

class Railroad(Property):
    def __init__(self,name,buyPrice,price):
        Property.__init__(self,name,buyPrice)
        self.price = price

    def getPrice(self,n):
        rrCount = 0
        for tile in self.owner.ownedTiles():
            if type(tile) == Railroad:
                rrCount+=1
        #print("RRGETPRICE:",int(self.price*(2**(rrCount-1))))
        return int(self.price*(2**(rrCount-1)))

class Utility(Property):
    def __init__(self,name,buyPrice,price):
        Property.__init__(self,name,buyPrice)
        self.price = price

    def getPrice(self,n):
        utiCount = 0
        for tile in self.owner.ownedTiles():
            if type(tile) == Utility:
                utiCount+=1
        return int(n*(self.price*2.5**(utiCount-1)))
