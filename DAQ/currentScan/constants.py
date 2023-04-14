T0 = 293.15 #T0 value for PT correction,  K
p0 = 970 #p0 value for PT correction, mbar

measTime = []
waitTime = []

measureInt = 2 #seconds, how often CAEN parameters are measured, also how often PT correction is executed

slot = [4,8] #HV slots
channels = [[5],[2,3]] #HV channels
effHV = [[] for x in range(len(slot))] #Effective HV

names = [[b"test-1"],[b"test-2",b"test-3"]]

caenIPaddress = "0.0.0.0"