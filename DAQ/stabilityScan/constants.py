T0 = 293.15 #T0 value for PT correction,  K
p0 = 970 #p0 value for PT correction, mbar

measTime = []
waitTime = []

measureInt = 2 #seconds, how often CAEN parameters are measured, also how often PT correction is executed

slot = [11,14] #HV slots
channels = [[2],[9,10]] #HV channels
#slot = [7,8] #HV slots
#channels = [[1,3,5],[3]] #HV channels

effHV = [[] for x in range(len(slot))] #Effective HV

names = [[b"testStab1"],[b"teststab2",b"testStab3"]]

caenIPaddress = "90.147.203.174"
