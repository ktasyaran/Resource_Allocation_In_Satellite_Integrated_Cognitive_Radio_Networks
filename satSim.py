#!/usr/bin/python3
import math
import random
import numpy
#Constant declaration.
GDR = 0.06
contents=100
totSat = 5
totTer = 10
c = 299792458
satBW = 36000000
terBW = 2000000
satFreq = 20000000000
terFreq = 700000000
gainSAT = 25000
gainBS = 0.00004
gainHU = 0.06
gainPUter = 0.11
radBS = 300
dSAT = 300000
dBS = 150
pSatTotal = 240
pBSTotal = 60
pchSat = pSatTotal / totSat
pchBS = pBSTotal / totTer
noiseSAT = 10 ** (-18)
noiseTER = 15 * (10 ** (-20))
baseMeanVal=25000000
enhMeanVal=5000000
renh=1
HUarr=0.3
SecArr=0.5
PriTerArr=0.8
PriSatArr=0.15
baseSizes=[]
enhSizes=[]
probArray=numpy.random.zipf(2,contents)
total=sum(probArray)
intervals=[]
simIter=1
simTime = 3600

#Base, enhancement and environment values. They provide start, end checking.
BASE_FAILURE=-1
BASE_SUC_EXIT=0
BASE_NOT_ENTER=1
BASE_RECEIVING=2

SAT_ENV=0
TER_ENV=1

ENH_NOT_ENTERED=1
ENH_RECEIVED=2
ENH_RECEIVING=3
ENH_FAILURE=4

#Generates ticket intervals for lottery.
for i in range(0,contents):
    if i==0:
        intervals.append(probArray[0])
    else:
        intervals.append(intervals[i-1]+probArray[i])


#Classes for different user types

"""Hybrid user"""
class Hybrid():
    def __init__(self,arrival,content):
        self.__title = "HU"
        self.__arrival=arrival
        self.__departure=0
        self.__baseStatus=BASE_NOT_ENTER
        self.__content=content
        self.__duration=0
        self.__enhStatus=ENH_NOT_ENTERED
        self.__environment=-1
        self.__remainingFrac=1.0

    def getFrac(self):
        return self.__remainingFrac
    def setRemainingFrac(self,newFrac):
        self.__remainingFrac=newFrac
    def setArrival(self,newArrival):
        self.__arrival=newArrival
    def getDuration(self):
        return self.__duration
    def setDuration(self,dur):
        self.__duration=dur
    def getEnvironment(self):
        return self.__environment
    def getEnhStatus(self):
        return self.__enhStatus
    def setEnvironment(self,newEnv):
        self.__environment=newEnv
    def getBaseStatus(self):
        return self.__baseStatus
    def getTitle(self):
        return self.__title
    def getArrival(self):
        return self.__arrival
    def setDeparture(self,departure):
        self.__departure=departure
    def getDeparture(self):
       return self.__departure
    def getContent(self):
        return self.__content
    def setBaseStatus(self,exit):
        self.__baseStatus=exit
    def setEnhStatus(self,newRec):
        self.__enhStatus=newRec

"""Secondary user"""
class Secondary():
    def __init__(self,arrival,content):
        self.__title = "SU"
        self.__arrival=arrival
        self.__departure=0
        self.__baseStatus = BASE_NOT_ENTER
        self.__content = content

    def getContent(self):
        return self.__content
    def getBaseStatus(self):
        return self.__baseStatus
    def getTitle(self):
        return self.__title
    def getArrival(self):
        return self.__arrival
    def setDeparture(self,departure):
        self.__departure=departure
    def getDeparture(self):
       return self.__departure
    def setBaseStatus(self,exit):
        self.__baseStatus=exit

"""Primary satellite user"""
class PrimarySat():
    def __init__(self,arrival,content):
        self.__title = "PU"
        self.__arrival=arrival
        self.__departure = 0
        self.__baseStatus = BASE_NOT_ENTER
        self.__content = content

    def getContent(self):
        return self.__content
    def getBaseStatus(self):
        return self.__baseStatus
    def getTitle(self):
        return self.__title
    def getArrival(self):
        return self.__arrival
    def setDeparture(self,departure):
        self.__departure=departure
    def getDeparture(self):
       return self.__departure
    def setBaseStatus(self,exit):
        self.__baseStatus=exit

"""Primary terrestrial user"""
class PrimaryTer():
    def __init__(self,arrival,content):
        self.__title = "PU"
        self.__arrival = arrival
        self.__departure = 0
        self.__baseStatus = BASE_NOT_ENTER
        self.__content = content

    def setBaseStatus(self,exit):
        self.__baseStatus=exit
    def getContent(self):
        return self.__content
    def getBaseStatus(self):
        return self.__baseStatus
    def getTitle(self):
        return self.__title
    def getArrival(self):
        return self.__arrival
    def setDeparture(self,departure):
        self.__departure=departure
    def getDeparture(self):
       return self.__departure

"""Longest Remaining time first algorithm for election (only for terrestrial channel)
If it is secondary, throw it, but if is hybrid, try to move satellite channel if possible if it is
not receiving enhancement. If receives enhancement, it is dropped.
"""
def eliminateSecondary(targetList,satLi,currentTime):
    index=-1
    iter=0
    min=0
    for item in targetList:
        remain = currentTime - item.getArrival()
        if item.getTitle()!="PU":
            if item.getTitle()=="HU":
                if item.getEnhStatus()==ENH_RECEIVING:
                        index=iter
                        break
                elif item.getEnhStatus()==ENH_NOT_ENTERED and item.getBaseStatus()==BASE_RECEIVING:
                    if remain > min:
                        min = remain
                        index = iter
            #Throw whenever primary sees first secondary
            else:
                    index=iter
                    break
        iter+=1

    if index>-1:
        if targetList[index].getTitle()=="HU":
            #If receiving enhancement
            if targetList[index].getEnhStatus()==ENH_RECEIVING:
                frac = (targetList[index].getFrac() * ((currentTime - targetList[index].getArrival())) / (targetList[index].getDuration()))
                targetList[index].setRemainingFrac(targetList[index].getFrac() - frac)
                targetList[index].setEnhStatus(ENH_FAILURE)
                targetList.remove(targetList[index])
            else:
                #If hybrid, tries for station Interchange from base to satellite
                if len(satLi)<totSat:
                    frac = (targetList[index].getFrac() * ((currentTime - targetList[index].getArrival())) / (targetList[index].getDuration()))
                    remaining = (targetList[index].getFrac() - frac) * (baseSizes[targetList[index].getContent() - 1])
                    newDur = math.ceil(remaining / HUSatcapacity(HUrecSatPower()))
                    targetList[index].setDeparture(currentTime + newDur)
                    targetList[index].setDuration(newDur)
                    targetList[index].setArrival(currentTime)
                    targetList[index].setEnvironment(SAT_ENV)
                    satLi.append(targetList[index])
                    targetList.remove(targetList[index])
                else:
                    targetList[index].setBaseStatus(BASE_FAILURE)
                    targetList.remove(targetList[index])
        #Eliminates if secondary directly.
        else:
            targetList[index].setBaseStatus(BASE_FAILURE)
            targetList.remove(targetList[index])



"""Power calculation functions depending on user type and enviromnent"""
def PUrecSatPower():
    return (pchSat * gainSAT * GDR * (c ** 2)) / ((4 * math.pi * satFreq * dSAT) ** 2)

def PUrecTerPower():
    return (pchBS * gainBS * gainPUter * (c ** 2)) / ((4 * math.pi * terFreq * dBS) ** 2)


def SUrecTerPower():
    return (pchBS * gainBS * GDR * (c ** 2)) / ((4 * math.pi * terFreq * dBS) ** 2)


def HUrecSatPower():
    return (pchSat * gainSAT * gainHU * (c ** 2)) / ((4 * math.pi * satFreq * dSAT) ** 2)


def HUrecBSPower():
    return (pchBS * gainBS * gainHU * (c ** 2)) / ((4 * math.pi * terFreq * dBS) ** 2)


#Functions for calculating Shannon Capacity

def PUSatcapacity(power):
    return satBW * math.log2(1 + ((power) / (noiseSAT * satBW)))


def PUTercapacity(power):
    return terBW * math.log2(1 + (power) / (noiseTER * terBW))


def SUTercapacity(power):
    return terBW * math.log2(1 + ((power) / (noiseTER * terBW)))


def HUSatcapacity(power):
    return satBW * math.log2(1 + ((power) / (noiseSAT * satBW)))


def HUBScapacity(power):
    return terBW * math.log2(1 + ((power) / (noiseTER * terBW)))

#User generation for different user types within simulation
def generateUsers():
    timer0=0
    timer1=0
    timer2=0
    timer3=0
    userHib = []
    userSec = []
    userPTer = []
    userPSat = []
    while timer0<=simTime:
        tempU=None
        content = lotterySchedule()
        if len(userHib)==0:
            tempU = Hybrid(numpy.random.poisson(1/HUarr), content)
        else:
            tempU = Hybrid(numpy.random.poisson(1/HUarr) + userHib[-1].getArrival(), content)
        userHib.append(tempU)
        timer0=userHib[-1].getArrival()
    while timer1<=simTime:
        tempU=None
        content = lotterySchedule()
        if len(userSec)==0:
            tempU = Secondary(numpy.random.poisson(1/SecArr), content)
        else:
            tempU = Secondary(numpy.random.poisson(1/SecArr) + userSec[-1].getArrival(), content)
        userSec.append(tempU)
        timer1=userSec[-1].getArrival()
    while timer2 <= simTime:
        tempU = None
        content = lotterySchedule()
        if len(userPTer) == 0:
            tempU = PrimaryTer(numpy.random.poisson(1 / PriTerArr), content)
        else:
            tempU = PrimaryTer(numpy.random.poisson(1 / PriTerArr) + userPTer[-1].getArrival(), content)
        userPTer.append(tempU)
        timer2 = userPTer[-1].getArrival()
    while timer3 <= simTime:
        tempU = None
        content = lotterySchedule()
        if len(userPSat) == 0:
            tempU = PrimarySat(numpy.random.poisson(1 / PriSatArr), content)
        else:
            tempU = PrimarySat(numpy.random.poisson(1 / PriSatArr) + userPSat[-1].getArrival(), content)
        userPSat.append(tempU)
        timer3 = userPSat[-1].getArrival()
    return [userHib,userSec,userPTer,userPSat]

#Generates content base end enhancement sizes. They will be fixed size.
def generateContents():
    for i in range(contents):
        baseSizes.append(random.expovariate(1.0 /baseMeanVal))
        enhSizes.append(random.expovariate(1.0 / enhMeanVal))

#Lottery scheduling algorithm for choosing contents per user.
def lotterySchedule():
    lottery = random.randint(1, total)
    winner = -1
    for i in range(0, contents):
        if lottery <= intervals[0]:
            winner = 0
            break
        else:
            if lottery >= intervals[i - 1] + 1 and lottery <= intervals[i]:
                winner = i
                break
    return winner+1


"""Removes all primary and secondary users. Also looks for enhancement statements.
If any idle channel exists, hybrid user can start receiving enhancement independent on 
its current environment. Environment interchange is also possible.
"""
def removeFinished(satChannel,terChannel,currentTime):
    HUSatIndices=[]
    HUBaseIndices=[]
    iter=0
    iter1=0
    for item in satChannel:
        if item.getDeparture()==currentTime:
            if item.getTitle()=="HU":
                if item.getEnhStatus()==ENH_RECEIVING:
                    item.setEnhStatus(ENH_RECEIVED)
                elif item.getBaseStatus()==BASE_RECEIVING:
                    item.setBaseStatus(BASE_SUC_EXIT)
                HUSatIndices.append(iter)
            else:
                item.setBaseStatus(BASE_SUC_EXIT)
        iter+=1
    newSatChannel=[item for item in satChannel if item.getBaseStatus()!=BASE_SUC_EXIT]
    for index in HUSatIndices:
        if satChannel[index].getEnhStatus()==ENH_NOT_ENTERED:
            if len(newSatChannel)<totSat:
                satChannel[index].setEnhStatus(ENH_RECEIVING)
                newDur=math.ceil(enhSizes[satChannel[index].getContent()-1]/HUSatcapacity(HUrecSatPower()))
                satChannel[index].setDuration(newDur)
                satChannel[index].setArrival(currentTime)
                satChannel[index].setDeparture(currentTime+newDur)
                satChannel[index].setRemainingFrac(1.0)
                newSatChannel.append(satChannel[index])

    for item in terChannel:
        if item.getDeparture()==currentTime:
            if item.getTitle()=="HU":
                if item.getEnhStatus()==ENH_RECEIVING:
                    item.setEnhStatus(ENH_RECEIVED)
                elif item.getBaseStatus()==BASE_RECEIVING:
                    item.setBaseStatus(BASE_SUC_EXIT)
                HUBaseIndices.append(iter1)
            else:
                item.setBaseStatus(BASE_SUC_EXIT)
        iter1+=1

    newTerChannel = [item for item in terChannel if item.getBaseStatus()!= BASE_SUC_EXIT]
    for index in HUBaseIndices:
        if terChannel[index].getEnhStatus() == ENH_NOT_ENTERED:
            if len(newTerChannel) < totTer:
                terChannel[index].setEnhStatus(ENH_RECEIVING)
                newDur = math.ceil(enhSizes[terChannel[index].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                terChannel[index].setDuration(newDur)
                terChannel[index].setArrival(currentTime)
                terChannel[index].setDeparture(currentTime + newDur)
                terChannel[index].setRemainingFrac(1.0)
                newTerChannel.append(terChannel[index])

    if len(newTerChannel) < totTer:
        for item in newSatChannel:
            if item.getTitle() == "HU":
                frac = (item.getFrac()*((currentTime - item.getArrival())) / (item.getDuration()))
                remaining = (item.getFrac() - frac) * (baseSizes[item.getContent() - 1])
                item.setEnvironment(TER_ENV)
                newDur = math.ceil(remaining / HUBScapacity(HUrecBSPower()))
                item.setDeparture(currentTime + newDur)
                item.setDuration(newDur)
                item.setRemainingFrac(item.getFrac() - frac)
                item.setArrival(currentTime)
                newSatChannel.remove(item)
                newTerChannel.append(item)

    return [newSatChannel,newTerChannel]

"""Throughput calculation for hybrid users."""
def calculateThroughputHU(userList):
    bps=0.0
    for i in range(0,len(userList)):
        if userList[i].getBaseStatus()==BASE_SUC_EXIT:
            bps+=baseSizes[userList[i].getContent()-1]
            if userList[i].getEnhStatus()!=ENH_NOT_ENTERED:
                bps+=enhSizes[userList[i].getContent()-1]*(1.0-userList[i].getFrac())
    return bps


def tryPlace(satChannel,terChannel,currentTime,currentEnv):
    index=-1
    iter=0
    min=0
    if currentEnv==SAT_ENV:
        for item in satChannel:
            difference=currentTime-item.getArrival()
            if item.getTitle()=="HU":
                if item.getEnhStatus()==ENH_RECEIVING:
                        index=iter
                        break
            iter+=1
        if index>-1:
            frac = (satChannel[index].getFrac() * ((currentTime - satChannel[index].getArrival())) / (satChannel[index].getDuration()))
            if len(terChannel)<totTer:
                remaining = (satChannel[index].getFrac() - frac) * (enhSizes[satChannel[index].getContent() - 1])
                satChannel[index].setEnvironment(TER_ENV)
                newDur = math.ceil(remaining / HUBScapacity(HUrecBSPower()))
                satChannel[index].setDeparture(currentTime + newDur)
                satChannel[index].setDuration(newDur)
                satChannel[index].setRemainingFrac(satChannel[index].getFrac() - frac)

                satChannel[index].setArrival(currentTime)
                terChannel.append(satChannel[index])
                satChannel.remove(satChannel[index])
            else:
                satChannel[index].setEnhStatus(ENH_FAILURE)
                satChannel.remove(satChannel[index])

    elif currentEnv==TER_ENV:
        for item in terChannel:
            difference=currentTime-item.getArrival()
            if item.getTitle()=="HU":
                #Throws first enhancement receiving hybrid
                if item.getEnhStatus()==ENH_RECEIVING:
                    if difference>min:
                        index=iter
                        min=difference
            iter+=1
        if index>-1:
            frac = (terChannel[index].getFrac() * ((currentTime - terChannel[index].getArrival())) / (terChannel[index].getDuration()))
            if len(satChannel) < totSat:
                remaining = (terChannel[index].getFrac() - frac) * (enhSizes[terChannel[index].getContent() - 1])
                terChannel[index].setEnvironment(SAT_ENV)
                newDur = math.ceil(remaining / HUSatcapacity(HUrecSatPower()))
                terChannel[index].setDeparture(currentTime + newDur)
                terChannel[index].setDuration(newDur)
                terChannel[index].setRemainingFrac(terChannel[index].getFrac() - frac)
                terChannel[index].setArrival(currentTime)
                satChannel.append(terChannel[index])
                terChannel.remove(terChannel[index])
            else:
                terChannel[index].setEnhStatus(ENH_FAILURE)
                terChannel.remove(terChannel[index])



# Designed random algorithm for simulation
def randomSimulate(userList):
    count = 0
    satList = []
    terList = []
    hibs = userList[0]
    secs = userList[1]
    pter = userList[2]
    psat = userList[3]
    while count < simTime:
        firstDelete=random.randint(1,2)

        if firstDelete==1:
            result = removeFinished(satList, terList, count)
            # New arrival lists for objects.
            satList = result[0]
            terList = result[1]
            firstLook=random.randint(1,4)
            if firstLook==1:
                for i in range(0, len(hibs)):
                    if hibs[i].getArrival() == count and hibs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                            hibs[i].setDeparture(duration + count)
                            hibs[i].setEnvironment(TER_ENV)
                            hibs[i].setBaseStatus(BASE_RECEIVING)
                            hibs[i].setDuration(duration)
                            terList.append(hibs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 5 and choice <= 7:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                                    hibs[i].setDeparture(duration + count)
                                    hibs[i].setEnvironment(TER_ENV)
                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                    hibs[i].setDuration(duration)
                                    terList.append(hibs[i])
                                else:
                                    choice1 = random.randint(1, 15)
                                    if choice1 >= 9 and choice1 <= 13:
                                        if len(satList) < totSat:
                                            duration = math.ceil(
                                                baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                                            hibs[i].setDeparture(duration + count)
                                            hibs[i].setEnvironment(SAT_ENV)
                                            hibs[i].setDuration(duration)
                                            hibs[i].setBaseStatus(BASE_RECEIVING)
                                            satList.append(hibs[i])
                                        else:
                                            choice2 = random.randint(1, 15)
                                            if choice2 >= 2 and choice2 <= 6:
                                                tryPlace(satList, terList, count, SAT_ENV)
                                                if len(satList) < totSat:
                                                    duration = math.ceil(
                                                        baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(
                                                            HUrecSatPower()))
                                                    hibs[i].setDeparture(duration + count)
                                                    hibs[i].setEnvironment(SAT_ENV)
                                                    hibs[i].setDuration(duration)
                                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                                    satList.append(hibs[i])
                                                else:
                                                    hibs[i].setBaseStatus(BASE_FAILURE)
                                            else:
                                                hibs[i].setBaseStatus(BASE_FAILURE)
                                    else:
                                        hibs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                hibs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(secs)):
                    if secs[i].getArrival() == count and secs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                            secs[i].setDeparture(duration + count)
                            secs[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(secs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 10 and choice <= 15:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                                    secs[i].setDeparture(duration + count)
                                    secs[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(secs[i])
                                else:
                                    secs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                secs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(psat)):
                    if psat[i].getArrival() == count and psat[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(satList) < totSat:
                            duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                            psat[i].setDeparture(duration + count)
                            psat[i].setBaseStatus(BASE_RECEIVING)
                            satList.append(psat[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 6 and choice <= 9:
                                tryPlace(satList, terList, count, SAT_ENV)
                                if len(satList) == totSat:
                                    psat[i].setBaseStatus(BASE_FAILURE)
                                else:
                                    duration = math.ceil(
                                        baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                                    psat[i].setDeparture(duration + count)
                                    satList.append(psat[i])
                                    psat[i].setBaseStatus(BASE_RECEIVING)
                            else:
                                psat[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(pter)):
                    if pter[i].getArrival() == count and pter[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                            pter[i].setDeparture(duration + count)
                            pter[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(pter[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 7 and choice <= 9:
                                eliminateSecondary(terList, satList, count)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                                    pter[i].setDeparture(duration + count)
                                    pter[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(pter[i])
                                else:
                                    pter[i].setBaseStatus(BASE_FAILURE)
                            else:
                                pter[i].setBaseStatus(BASE_FAILURE)
            elif firstLook==2:

                for i in range(0, len(secs)):
                    if secs[i].getArrival() == count and secs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                            secs[i].setDeparture(duration + count)
                            secs[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(secs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 10 and choice <= 15:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                                    secs[i].setDeparture(duration + count)
                                    secs[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(secs[i])
                                else:
                                    secs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                secs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(hibs)):
                    if hibs[i].getArrival() == count and hibs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                            hibs[i].setDeparture(duration + count)
                            hibs[i].setEnvironment(TER_ENV)
                            hibs[i].setBaseStatus(BASE_RECEIVING)
                            hibs[i].setDuration(duration)
                            terList.append(hibs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 5 and choice <= 7:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                                    hibs[i].setDeparture(duration + count)
                                    hibs[i].setEnvironment(TER_ENV)
                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                    hibs[i].setDuration(duration)
                                    terList.append(hibs[i])
                                else:
                                    choice1 = random.randint(1, 15)
                                    if choice1 >= 9 and choice1 <= 13:
                                        if len(satList) < totSat:
                                            duration = math.ceil(
                                                baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                                            hibs[i].setDeparture(duration + count)
                                            hibs[i].setEnvironment(SAT_ENV)
                                            hibs[i].setDuration(duration)
                                            hibs[i].setBaseStatus(BASE_RECEIVING)
                                            satList.append(hibs[i])
                                        else:
                                            choice2 = random.randint(1, 15)
                                            if choice2 >= 2 and choice2 <= 6:
                                                tryPlace(satList, terList, count, SAT_ENV)
                                                if len(satList) < totSat:
                                                    duration = math.ceil(
                                                        baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(
                                                            HUrecSatPower()))
                                                    hibs[i].setDeparture(duration + count)
                                                    hibs[i].setEnvironment(SAT_ENV)
                                                    hibs[i].setDuration(duration)
                                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                                    satList.append(hibs[i])
                                                else:
                                                    hibs[i].setBaseStatus(BASE_FAILURE)
                                            else:
                                                hibs[i].setBaseStatus(BASE_FAILURE)
                                    else:
                                        hibs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                hibs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(psat)):
                    if psat[i].getArrival() == count and psat[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(satList) < totSat:
                            duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                            psat[i].setDeparture(duration + count)
                            psat[i].setBaseStatus(BASE_RECEIVING)
                            satList.append(psat[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 6 and choice <= 9:
                                tryPlace(satList, terList, count, SAT_ENV)
                                if len(satList) == totSat:
                                    psat[i].setBaseStatus(BASE_FAILURE)
                                else:
                                    duration = math.ceil(
                                        baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                                    psat[i].setDeparture(duration + count)
                                    satList.append(psat[i])
                                    psat[i].setBaseStatus(BASE_RECEIVING)
                            else:
                                psat[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(pter)):
                    if pter[i].getArrival() == count and pter[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                            pter[i].setDeparture(duration + count)
                            pter[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(pter[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 7 and choice <= 9:
                                eliminateSecondary(terList, satList, count)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                                    pter[i].setDeparture(duration + count)
                                    pter[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(pter[i])
                                else:
                                    pter[i].setBaseStatus(BASE_FAILURE)
                            else:
                                pter[i].setBaseStatus(BASE_FAILURE)
            elif firstLook == 3:
                for i in range(0, len(psat)):
                    if psat[i].getArrival() == count and psat[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(satList) < totSat:
                            duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                            psat[i].setDeparture(duration + count)
                            psat[i].setBaseStatus(BASE_RECEIVING)
                            satList.append(psat[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 6 and choice <= 9:
                                tryPlace(satList, terList, count, SAT_ENV)
                                if len(satList) == totSat:
                                    psat[i].setBaseStatus(BASE_FAILURE)
                                else:
                                    duration = math.ceil(
                                        baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                                    psat[i].setDeparture(duration + count)
                                    satList.append(psat[i])
                                    psat[i].setBaseStatus(BASE_RECEIVING)
                            else:
                                psat[i].setBaseStatus(BASE_FAILURE)

                for i in range(0, len(hibs)):
                    if hibs[i].getArrival() == count and hibs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                            hibs[i].setDeparture(duration + count)
                            hibs[i].setEnvironment(TER_ENV)
                            hibs[i].setBaseStatus(BASE_RECEIVING)
                            hibs[i].setDuration(duration)
                            terList.append(hibs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 5 and choice <= 7:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                                    hibs[i].setDeparture(duration + count)
                                    hibs[i].setEnvironment(TER_ENV)
                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                    hibs[i].setDuration(duration)
                                    terList.append(hibs[i])
                                else:
                                    choice1 = random.randint(1, 15)
                                    if choice1 >= 9 and choice1 <= 13:
                                        if len(satList) < totSat:
                                            duration = math.ceil(
                                                baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                                            hibs[i].setDeparture(duration + count)
                                            hibs[i].setEnvironment(SAT_ENV)
                                            hibs[i].setDuration(duration)
                                            hibs[i].setBaseStatus(BASE_RECEIVING)
                                            satList.append(hibs[i])
                                        else:
                                            choice2 = random.randint(1, 15)
                                            if choice2 >= 2 and choice2 <= 6:
                                                tryPlace(satList, terList, count, SAT_ENV)
                                                if len(satList) < totSat:
                                                    duration = math.ceil(
                                                        baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(
                                                            HUrecSatPower()))
                                                    hibs[i].setDeparture(duration + count)
                                                    hibs[i].setEnvironment(SAT_ENV)
                                                    hibs[i].setDuration(duration)
                                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                                    satList.append(hibs[i])
                                                else:
                                                    hibs[i].setBaseStatus(BASE_FAILURE)
                                            else:
                                                hibs[i].setBaseStatus(BASE_FAILURE)
                                    else:
                                        hibs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                hibs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(secs)):
                    if secs[i].getArrival() == count and secs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                            secs[i].setDeparture(duration + count)
                            secs[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(secs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 10 and choice <= 15:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                                    secs[i].setDeparture(duration + count)
                                    secs[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(secs[i])
                                else:
                                    secs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                secs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(pter)):
                    if pter[i].getArrival() == count and pter[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                            pter[i].setDeparture(duration + count)
                            pter[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(pter[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 7 and choice <= 9:
                                eliminateSecondary(terList, satList, count)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                                    pter[i].setDeparture(duration + count)
                                    pter[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(pter[i])
                                else:
                                    pter[i].setBaseStatus(BASE_FAILURE)
                            else:
                                pter[i].setBaseStatus(BASE_FAILURE)
            elif firstLook == 4:
                for i in range(0, len(pter)):
                    if pter[i].getArrival() == count and pter[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                            pter[i].setDeparture(duration + count)
                            pter[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(pter[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 7 and choice <= 9:
                                eliminateSecondary(terList, satList, count)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                                    pter[i].setDeparture(duration + count)
                                    pter[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(pter[i])
                                else:
                                    pter[i].setBaseStatus(BASE_FAILURE)
                            else:
                                pter[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(hibs)):
                    if hibs[i].getArrival() == count and hibs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                            hibs[i].setDeparture(duration + count)
                            hibs[i].setEnvironment(TER_ENV)
                            hibs[i].setBaseStatus(BASE_RECEIVING)
                            hibs[i].setDuration(duration)
                            terList.append(hibs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 5 and choice <= 7:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                                    hibs[i].setDeparture(duration + count)
                                    hibs[i].setEnvironment(TER_ENV)
                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                    hibs[i].setDuration(duration)
                                    terList.append(hibs[i])
                                else:
                                    choice1 = random.randint(1, 15)
                                    if choice1 >= 9 and choice1 <= 13:
                                        if len(satList) < totSat:
                                            duration = math.ceil(
                                                baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                                            hibs[i].setDeparture(duration + count)
                                            hibs[i].setEnvironment(SAT_ENV)
                                            hibs[i].setDuration(duration)
                                            hibs[i].setBaseStatus(BASE_RECEIVING)
                                            satList.append(hibs[i])
                                        else:
                                            choice2 = random.randint(1, 15)
                                            if choice2 >= 2 and choice2 <= 6:
                                                tryPlace(satList, terList, count, SAT_ENV)
                                                if len(satList) < totSat:
                                                    duration = math.ceil(
                                                        baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(
                                                            HUrecSatPower()))
                                                    hibs[i].setDeparture(duration + count)
                                                    hibs[i].setEnvironment(SAT_ENV)
                                                    hibs[i].setDuration(duration)
                                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                                    satList.append(hibs[i])
                                                else:
                                                    hibs[i].setBaseStatus(BASE_FAILURE)
                                            else:
                                                hibs[i].setBaseStatus(BASE_FAILURE)
                                    else:
                                        hibs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                hibs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(secs)):
                    if secs[i].getArrival() == count and secs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                            secs[i].setDeparture(duration + count)
                            secs[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(secs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 10 and choice <= 15:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                                    secs[i].setDeparture(duration + count)
                                    secs[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(secs[i])
                                else:
                                    secs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                secs[i].setBaseStatus(BASE_FAILURE)

                for i in range(0, len(psat)):
                    if psat[i].getArrival() == count and psat[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(satList) < totSat:
                            duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                            psat[i].setDeparture(duration + count)
                            psat[i].setBaseStatus(BASE_RECEIVING)
                            satList.append(psat[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 6 and choice <= 9:
                                tryPlace(satList, terList, count, SAT_ENV)
                                if len(satList) == totSat:
                                    psat[i].setBaseStatus(BASE_FAILURE)
                                else:
                                    duration = math.ceil(
                                        baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                                    psat[i].setDeparture(duration + count)
                                    satList.append(psat[i])
                                    psat[i].setBaseStatus(BASE_RECEIVING)
                            else:
                                psat[i].setBaseStatus(BASE_FAILURE)

        else:
            firstLook = random.randint(1, 4)
            if firstLook == 1:
                for i in range(0, len(hibs)):
                    if hibs[i].getArrival() == count and hibs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                            hibs[i].setDeparture(duration + count)
                            hibs[i].setEnvironment(TER_ENV)
                            hibs[i].setBaseStatus(BASE_RECEIVING)
                            hibs[i].setDuration(duration)
                            terList.append(hibs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 5 and choice <= 7:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                                    hibs[i].setDeparture(duration + count)
                                    hibs[i].setEnvironment(TER_ENV)
                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                    hibs[i].setDuration(duration)
                                    terList.append(hibs[i])
                                else:
                                    choice1 = random.randint(1, 15)
                                    if choice1 >= 9 and choice1 <= 13:
                                        if len(satList) < totSat:
                                            duration = math.ceil(
                                                baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                                            hibs[i].setDeparture(duration + count)
                                            hibs[i].setEnvironment(SAT_ENV)
                                            hibs[i].setDuration(duration)
                                            hibs[i].setBaseStatus(BASE_RECEIVING)
                                            satList.append(hibs[i])
                                        else:
                                            choice2 = random.randint(1, 15)
                                            if choice2 >= 2 and choice2 <= 6:
                                                tryPlace(satList, terList, count, SAT_ENV)
                                                if len(satList) < totSat:
                                                    duration = math.ceil(
                                                        baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(
                                                            HUrecSatPower()))
                                                    hibs[i].setDeparture(duration + count)
                                                    hibs[i].setEnvironment(SAT_ENV)
                                                    hibs[i].setDuration(duration)
                                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                                    satList.append(hibs[i])
                                                else:
                                                    hibs[i].setBaseStatus(BASE_FAILURE)
                                            else:
                                                hibs[i].setBaseStatus(BASE_FAILURE)
                                    else:
                                        hibs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                hibs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(secs)):
                    if secs[i].getArrival() == count and secs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                            secs[i].setDeparture(duration + count)
                            secs[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(secs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 10 and choice <= 15:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                                    secs[i].setDeparture(duration + count)
                                    secs[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(secs[i])
                                else:
                                    secs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                secs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(psat)):
                    if psat[i].getArrival() == count and psat[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(satList) < totSat:
                            duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                            psat[i].setDeparture(duration + count)
                            psat[i].setBaseStatus(BASE_RECEIVING)
                            satList.append(psat[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 6 and choice <= 9:
                                tryPlace(satList, terList, count, SAT_ENV)
                                if len(satList) == totSat:
                                    psat[i].setBaseStatus(BASE_FAILURE)
                                else:
                                    duration = math.ceil(
                                        baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                                    psat[i].setDeparture(duration + count)
                                    satList.append(psat[i])
                                    psat[i].setBaseStatus(BASE_RECEIVING)
                            else:
                                psat[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(pter)):
                    if pter[i].getArrival() == count and pter[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                            pter[i].setDeparture(duration + count)
                            pter[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(pter[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 7 and choice <= 9:
                                eliminateSecondary(terList, satList, count)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                                    pter[i].setDeparture(duration + count)
                                    pter[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(pter[i])
                                else:
                                    pter[i].setBaseStatus(BASE_FAILURE)
                            else:
                                pter[i].setBaseStatus(BASE_FAILURE)
            elif firstLook == 2:

                for i in range(0, len(secs)):
                    if secs[i].getArrival() == count and secs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                            secs[i].setDeparture(duration + count)
                            secs[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(secs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 10 and choice <= 15:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                                    secs[i].setDeparture(duration + count)
                                    secs[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(secs[i])
                                else:
                                    secs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                secs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(hibs)):
                    if hibs[i].getArrival() == count and hibs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                            hibs[i].setDeparture(duration + count)
                            hibs[i].setEnvironment(TER_ENV)
                            hibs[i].setBaseStatus(BASE_RECEIVING)
                            hibs[i].setDuration(duration)
                            terList.append(hibs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 5 and choice <= 7:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                                    hibs[i].setDeparture(duration + count)
                                    hibs[i].setEnvironment(TER_ENV)
                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                    hibs[i].setDuration(duration)
                                    terList.append(hibs[i])
                                else:
                                    choice1 = random.randint(1, 15)
                                    if choice1 >= 9 and choice1 <= 13:
                                        if len(satList) < totSat:
                                            duration = math.ceil(
                                                baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                                            hibs[i].setDeparture(duration + count)
                                            hibs[i].setEnvironment(SAT_ENV)
                                            hibs[i].setDuration(duration)
                                            hibs[i].setBaseStatus(BASE_RECEIVING)
                                            satList.append(hibs[i])
                                        else:
                                            choice2 = random.randint(1, 15)
                                            if choice2 >= 2 and choice2 <= 6:
                                                tryPlace(satList, terList, count, SAT_ENV)
                                                if len(satList) < totSat:
                                                    duration = math.ceil(
                                                        baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(
                                                            HUrecSatPower()))
                                                    hibs[i].setDeparture(duration + count)
                                                    hibs[i].setEnvironment(SAT_ENV)
                                                    hibs[i].setDuration(duration)
                                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                                    satList.append(hibs[i])
                                                else:
                                                    hibs[i].setBaseStatus(BASE_FAILURE)
                                            else:
                                                hibs[i].setBaseStatus(BASE_FAILURE)
                                    else:
                                        hibs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                hibs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(psat)):
                    if psat[i].getArrival() == count and psat[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(satList) < totSat:
                            duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                            psat[i].setDeparture(duration + count)
                            psat[i].setBaseStatus(BASE_RECEIVING)
                            satList.append(psat[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 6 and choice <= 9:
                                tryPlace(satList, terList, count, SAT_ENV)
                                if len(satList) == totSat:
                                    psat[i].setBaseStatus(BASE_FAILURE)
                                else:
                                    duration = math.ceil(
                                        baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                                    psat[i].setDeparture(duration + count)
                                    satList.append(psat[i])
                                    psat[i].setBaseStatus(BASE_RECEIVING)
                            else:
                                psat[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(pter)):
                    if pter[i].getArrival() == count and pter[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                            pter[i].setDeparture(duration + count)
                            pter[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(pter[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 7 and choice <= 9:
                                eliminateSecondary(terList, satList, count)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                                    pter[i].setDeparture(duration + count)
                                    pter[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(pter[i])
                                else:
                                    pter[i].setBaseStatus(BASE_FAILURE)
                            else:
                                pter[i].setBaseStatus(BASE_FAILURE)
            elif firstLook == 3:
                for i in range(0, len(psat)):
                    if psat[i].getArrival() == count and psat[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(satList) < totSat:
                            duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                            psat[i].setDeparture(duration + count)
                            psat[i].setBaseStatus(BASE_RECEIVING)
                            satList.append(psat[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 6 and choice <= 9:
                                tryPlace(satList, terList, count, SAT_ENV)
                                if len(satList) == totSat:
                                    psat[i].setBaseStatus(BASE_FAILURE)
                                else:
                                    duration = math.ceil(
                                        baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                                    psat[i].setDeparture(duration + count)
                                    satList.append(psat[i])
                                    psat[i].setBaseStatus(BASE_RECEIVING)
                            else:
                                psat[i].setBaseStatus(BASE_FAILURE)

                for i in range(0, len(hibs)):
                    if hibs[i].getArrival() == count and hibs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                            hibs[i].setDeparture(duration + count)
                            hibs[i].setEnvironment(TER_ENV)
                            hibs[i].setBaseStatus(BASE_RECEIVING)
                            hibs[i].setDuration(duration)
                            terList.append(hibs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 5 and choice <= 7:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                                    hibs[i].setDeparture(duration + count)
                                    hibs[i].setEnvironment(TER_ENV)
                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                    hibs[i].setDuration(duration)
                                    terList.append(hibs[i])
                                else:
                                    choice1 = random.randint(1, 15)
                                    if choice1 >= 9 and choice1 <= 13:
                                        if len(satList) < totSat:
                                            duration = math.ceil(
                                                baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                                            hibs[i].setDeparture(duration + count)
                                            hibs[i].setEnvironment(SAT_ENV)
                                            hibs[i].setDuration(duration)
                                            hibs[i].setBaseStatus(BASE_RECEIVING)
                                            satList.append(hibs[i])
                                        else:
                                            choice2 = random.randint(1, 15)
                                            if choice2 >= 2 and choice2 <= 6:
                                                tryPlace(satList, terList, count, SAT_ENV)
                                                if len(satList) < totSat:
                                                    duration = math.ceil(
                                                        baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(
                                                            HUrecSatPower()))
                                                    hibs[i].setDeparture(duration + count)
                                                    hibs[i].setEnvironment(SAT_ENV)
                                                    hibs[i].setDuration(duration)
                                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                                    satList.append(hibs[i])
                                                else:
                                                    hibs[i].setBaseStatus(BASE_FAILURE)
                                            else:
                                                hibs[i].setBaseStatus(BASE_FAILURE)
                                    else:
                                        hibs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                hibs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(secs)):
                    if secs[i].getArrival() == count and secs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                            secs[i].setDeparture(duration + count)
                            secs[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(secs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 10 and choice <= 15:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                                    secs[i].setDeparture(duration + count)
                                    secs[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(secs[i])
                                else:
                                    secs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                secs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(pter)):
                    if pter[i].getArrival() == count and pter[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                            pter[i].setDeparture(duration + count)
                            pter[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(pter[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 7 and choice <= 9:
                                eliminateSecondary(terList, satList, count)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                                    pter[i].setDeparture(duration + count)
                                    pter[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(pter[i])
                                else:
                                    pter[i].setBaseStatus(BASE_FAILURE)
                            else:
                                pter[i].setBaseStatus(BASE_FAILURE)
            elif firstLook == 4:
                for i in range(0, len(pter)):
                    if pter[i].getArrival() == count and pter[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                            pter[i].setDeparture(duration + count)
                            pter[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(pter[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 7 and choice <= 9:
                                eliminateSecondary(terList, satList, count)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                                    pter[i].setDeparture(duration + count)
                                    pter[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(pter[i])
                                else:
                                    pter[i].setBaseStatus(BASE_FAILURE)
                            else:
                                pter[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(hibs)):
                    if hibs[i].getArrival() == count and hibs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                            hibs[i].setDeparture(duration + count)
                            hibs[i].setEnvironment(TER_ENV)
                            hibs[i].setBaseStatus(BASE_RECEIVING)
                            hibs[i].setDuration(duration)
                            terList.append(hibs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 5 and choice <= 7:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[hibs[i].getContent() - 1] / HUBScapacity(HUrecBSPower()))
                                    hibs[i].setDeparture(duration + count)
                                    hibs[i].setEnvironment(TER_ENV)
                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                    hibs[i].setDuration(duration)
                                    terList.append(hibs[i])
                                else:
                                    choice1 = random.randint(1, 15)
                                    if choice1 >= 9 and choice1 <= 13:
                                        if len(satList) < totSat:
                                            duration = math.ceil(
                                                baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                                            hibs[i].setDeparture(duration + count)
                                            hibs[i].setEnvironment(SAT_ENV)
                                            hibs[i].setDuration(duration)
                                            hibs[i].setBaseStatus(BASE_RECEIVING)
                                            satList.append(hibs[i])
                                        else:
                                            choice2 = random.randint(1, 15)
                                            if choice2 >= 2 and choice2 <= 6:
                                                tryPlace(satList, terList, count, SAT_ENV)
                                                if len(satList) < totSat:
                                                    duration = math.ceil(
                                                        baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(
                                                            HUrecSatPower()))
                                                    hibs[i].setDeparture(duration + count)
                                                    hibs[i].setEnvironment(SAT_ENV)
                                                    hibs[i].setDuration(duration)
                                                    hibs[i].setBaseStatus(BASE_RECEIVING)
                                                    satList.append(hibs[i])
                                                else:
                                                    hibs[i].setBaseStatus(BASE_FAILURE)
                                            else:
                                                hibs[i].setBaseStatus(BASE_FAILURE)
                                    else:
                                        hibs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                hibs[i].setBaseStatus(BASE_FAILURE)
                for i in range(0, len(secs)):
                    if secs[i].getArrival() == count and secs[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(terList) < totTer:
                            duration = math.ceil(baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                            secs[i].setDeparture(duration + count)
                            secs[i].setBaseStatus(BASE_RECEIVING)
                            terList.append(secs[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 10 and choice <= 15:
                                tryPlace(satList, terList, count, TER_ENV)
                                if len(terList) < totTer:
                                    duration = math.ceil(
                                        baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                                    secs[i].setDeparture(duration + count)
                                    secs[i].setBaseStatus(BASE_RECEIVING)
                                    terList.append(secs[i])
                                else:
                                    secs[i].setBaseStatus(BASE_FAILURE)
                            else:
                                secs[i].setBaseStatus(BASE_FAILURE)

                for i in range(0, len(psat)):
                    if psat[i].getArrival() == count and psat[i].getBaseStatus() == BASE_NOT_ENTER:
                        if len(satList) < totSat:
                            duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                            psat[i].setDeparture(duration + count)
                            psat[i].setBaseStatus(BASE_RECEIVING)
                            satList.append(psat[i])
                        else:
                            choice = random.randint(1, 15)
                            if choice >= 6 and choice <= 9:
                                tryPlace(satList, terList, count, SAT_ENV)
                                if len(satList) == totSat:
                                    psat[i].setBaseStatus(BASE_FAILURE)
                                else:
                                    duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                                    psat[i].setDeparture(duration + count)
                                    satList.append(psat[i])
                                    psat[i].setBaseStatus(BASE_RECEIVING)
                            else:
                                psat[i].setBaseStatus(BASE_FAILURE)
            result = removeFinished(satList, terList, count)
            # New arrival lists for objects.
            satList = result[0]
            terList = result[1]
        count += simIter


# User- Designed algorithm simulation
def myAlgoSimulate(userList):
    count = 0
    satList = []
    terList = []
    # [userHib,userSec,userPTer,userPSat]
    hibs = userList[0]
    secs = userList[1]
    pter = userList[2]
    psat = userList[3]
    # Event simulation for users. Secondary and hybrid remains
    while count < simTime:
        result=removeFinished(satList,terList,count)
        #New arrival lists for objects.
        satList=result[0]
        terList=result[1]

        for i in range(0,len(hibs)):
            if hibs[i].getArrival()==count and hibs[i].getBaseStatus()==BASE_NOT_ENTER:
                if len(terList)<totTer:
                    duration=math.ceil(baseSizes[hibs[i].getContent()-1]/HUBScapacity(HUrecBSPower()))
                    hibs[i].setDeparture(duration+count)
                    hibs[i].setEnvironment(TER_ENV)
                    hibs[i].setBaseStatus(BASE_RECEIVING)
                    hibs[i].setDuration(duration)
                    terList.append(hibs[i])
                else:
                    if len(satList)<totSat:
                        duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                        hibs[i].setDeparture(duration + count)
                        hibs[i].setEnvironment(SAT_ENV)
                        hibs[i].setDuration(duration)
                        hibs[i].setBaseStatus(BASE_RECEIVING)
                        satList.append(hibs[i])
                    else:
                        tryPlace(satList,terList,count,SAT_ENV)
                        if len(satList)<totSat:
                            duration = math.ceil(baseSizes[hibs[i].getContent() - 1] / HUSatcapacity(HUrecSatPower()))
                            hibs[i].setDeparture(duration + count)
                            hibs[i].setEnvironment(SAT_ENV)
                            hibs[i].setDuration(duration)
                            hibs[i].setBaseStatus(BASE_RECEIVING)
                            satList.append(hibs[i])
                        else:
                            hibs[i].setBaseStatus(BASE_FAILURE)
        for i in range(0,len(secs)):
            if len(terList) < totTer:
                duration = math.ceil(baseSizes[secs[i].getContent() - 1] / SUTercapacity(SUrecTerPower()))
                secs[i].setDeparture(duration + count)
                secs[i].setBaseStatus(BASE_RECEIVING)
                terList.append(secs[i])
            else:
                secs[i].setBaseStatus(BASE_FAILURE)

        for i in range(0,len(psat)):
            if psat[i].getArrival()==count and psat[i].getBaseStatus()==BASE_NOT_ENTER:
                if len(satList)<totSat:
                    duration = math.ceil(baseSizes[psat[i].getContent() - 1] / PUSatcapacity(PUrecSatPower()))
                    psat[i].setDeparture(duration + count)
                    psat[i].setBaseStatus(BASE_RECEIVING)
                    satList.append(psat[i])
                else:
                    psat[i].setBaseStatus(BASE_FAILURE)
        for i in range(0,len(pter)):
            if pter[i].getArrival()==count and pter[i].getBaseStatus()==BASE_NOT_ENTER:
                if len(terList)<totTer:
                    duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                    pter[i].setDeparture(duration + count)
                    pter[i].setBaseStatus(BASE_RECEIVING)
                    terList.append(pter[i])
                else:
                    eliminateSecondary(terList,satList,count)
                    if len(terList)<totTer:
                        duration = math.ceil(baseSizes[pter[i].getContent() - 1] / PUTercapacity(PUrecTerPower()))
                        pter[i].setDeparture(duration + count)
                        pter[i].setBaseStatus(BASE_RECEIVING)
                        terList.append(pter[i])
                    else:
                        pter[i].setBaseStatus(BASE_FAILURE)

        count += simIter


