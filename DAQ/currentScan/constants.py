T0 = 293.15 #T0 value for PT correction,  K
p0 = 970 #p0 value for PT correction, mbar
corrTime = 5 #seconds, perform PT correction every corrTime s

effHV = []
measTime = []
waitTime = []

measureInt = 2

#slot = [4,8]
#channels = [[1],[2,3]] #HV channels

slot = [8]
channels = [[2,3]] #HV channels

caenIPaddress = "0.0.0.0"