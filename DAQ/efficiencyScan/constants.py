T0 = 293.15 #T0 value for PT correction,  K
p0 = 970 #p0 value for PT correction, mbar

measTime = []
waitTime = []

measureInt = 2 #seconds, how often CAEN parameters are measured, also how often PT correction is executed

slot = [7] #HV slots
channels = [[1]] #HV channels
#slot = [7,8] #HV slots
#channels = [[1],[3]] #HV channels

effHV = [[] for x in range(len(slot))] #Effective HV

names = [[b"ECOgas"]]

caenIPaddress = "90.147.203.174"
