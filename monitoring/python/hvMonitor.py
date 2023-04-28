#File to monitor hv and current of given HV channel in CAEN HV module
#Save HV and current values every 30 seconds
import sys #To perform system operation
sys.path.insert(0, '/home/pcald32/labStrada/DAQ/currentScan') #import CAEN.py file from currentScan folder

#import constants #constants
from CAEN import CAEN
#import numpy as np #numpy
#import ctypes #for C++ function binding (CAEN HV library for example)
#import pathlib #for library paths (to use C++ libraries in python)
#import mysql.connector #to connect to db to send the data
#import ROOT #Root CERN functions
import time #For functions such as sleep
import datetime #To get date, time and perform operations on them
#import os #To create new folders and so on

debug = True

def main():
    print("---HV monitor starting---")

    alive = 0

    print("Getting configuration file")

    with open("/home/pcald32/labStrada/config/monitoringConfig.txt") as configFile:
        scanPoints = configFile.readlines()
        scanPoints.pop(0)
        
        if debug:
            print(scanPoints)

        for point in scanPoints:
            asList = point.split("\t")
            length = len(asList)

            iCh = 0
            for slot in range(len(slots)):
                for channel in enumerate(channels[slot]):
                    effHV[slot].append(asList[iCh])
                    iCh = iCh+1

            constants.measTime.append(asList[length-2])
            constants.waitTime.append(asList[length-1].replace("\n", ""))

    if debug:
        print(effHV)

    #Infinite loop to monitor HV and current
    #Connect and disconnect every time from the HV module to not
    #keep the connection busy for too long
    while True:
        print("---Alive counter:",alive,"---")
        
        #Connect to HV module
        hvModule = CAEN(b"90.147.203.174",b"admin",b"admin")
        handle = hvModule.connect()
        print("handle in main",handle)

        hvModule.disconnect(handle)

        alive = alive+1
        time.sleep(30)

if __name__ == "__main__":
    main()