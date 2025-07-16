T0 = 293.15 #T0 value for PT correction,  K
p0 = 990 #p0 value for PT correction, mbar

measTime = []
waitTime = []

measureInt = 2 #seconds, how often CAEN parameters are measured, also how often PT correction is executed

slot = [8] #HV slots
channels = [[2]] #HV channels
#slot = [7,8] #HV slots
#channels = [[1,3,5],[3]] #HV channels

effHV = [[] for x in range(len(slot))] #Effective HV

names = [[b"ALICE-2-2"]]

caenIPaddress = "128.141.151.206"
