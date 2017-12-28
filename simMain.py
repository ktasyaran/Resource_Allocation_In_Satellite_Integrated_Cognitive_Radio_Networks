#!/usr/bin/python3
import satSim as SaS
import copy
"""Main program. Simulation starts here."""
userAlgTot=0.0
userRandTot=0.0
for i in range(1,11):
    SaS.generateContents()
    users=SaS.generateUsers()
    users1=[]
    for i in range (0,len(users)):
        users1.append(copy.deepcopy(users[i]))
    SaS.myAlgoSimulate(users)
    SaS.randomSimulate(users1)
    res=SaS.calculateThroughputHU(users[0])
    res1=SaS.calculateThroughputHU(users1[0])
    userAlgTot+= res/SaS.simTime
    userRandTot += res1 / SaS.simTime
print("Simulation repetition time: "+str(10))
print("Designed algorithm average: "+str(userAlgTot/10))
print("Random algorithm average: "+str(userRandTot/10))
