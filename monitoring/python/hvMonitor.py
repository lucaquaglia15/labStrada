#File to monitor hv and current of given HV channel in CAEN HV module
#Save HV and current values every 30 seconds
import constants #constants
import sys #To perform system operation
sys.path.insert(0, '/home/pcald32/labStrada/DAQ/currentScan') #import CAEN.py file from currentScan folder

from CAEN import CAEN
#import numpy as np #numpy
#import ctypes #for C++ function binding (CAEN HV library for example)
#import pathlib #for library paths (to use C++ libraries in python)
import mysql.connector #to connect to db to send the data
#import ROOT #Root CERN functions
import time #For functions such as sleep
import datetime #To get date, time and perform operations on them
#import os #To create new folders and so on

debug = True

def main():
    print("---HV monitor starting---")
    alive = 0

    #connect to mysql db
    mydb = mysql.connector.connect( #db object
        host="localhost",
        user="root",
        password="pcald32",
        database="labStrada"
    )
    mycursor = mydb.cursor()

    #Get values from constants.py
    slots = []
    slots = constants.slot #HV module slots
    channels = []
    channels = constants.channels #HV channels

    #Infinite loop to monitor HV and current
    #Connect and disconnect every time from the HV module to not
    #keep the connection busy for too long
    while True:
        print("---Alive counter:",alive,"---")
        
        #Connect to HV module
        hvModule = CAEN(b"90.147.203.174",b"admin",b"admin")
        handle = hvModule.connect()
        print("handle in main",handle)

        #Get CAEN HV data
        for slot in range(len(slots)):
            for iCh, channel in enumerate(channels[slot]):
                print("Slot",slots[slot],"channel",channel)
                hvMon = hvModule.getParameter(handle,slots[slot],b"VMon",channel)
                iMon = hvModule.getParameter(handle,slots[slot],b"IMon",channel)
                hvSet = hvModule.getParameter(handle,slots[slot],b"V0Set",channel)
                name = hvModule.getChName(handle,slots[slot],channel)
                hvEff = 0  #Just a test since PMTs have no effective HV
                #print("ch name",name)

                #insert into db
                val = (slots[slot],channel,name,hvSet,hvMon,hvEff,iMon)

                hvMonitorQuery = "INSERT INTO CAEN (slot,channel,chName,hvSet,hvMon,hvEff,iMon) VALUES (%s, %s, %s, %s, %s, %s, %s)" #sql query
                mycursor.execute(hvMonitorQuery, val)

                mydb.commit() #execute query

        hvModule.disconnect(handle)

        alive = alive+1
        time.sleep(10)

if __name__ == "__main__":
    main()