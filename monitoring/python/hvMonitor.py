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
from dotenv import dotenv_values

debug = True

def main():
    print("---HV monitor starting---")
    alive = 0

    secrets = dotenv_values("/home/pcald32/labStrada/.env")

    mydb = mysql.connector.connect( #db object on localhost
        host=secrets["host"],
        user=secrets["user"],
        password=secrets["password"],
        database=secrets["database"]
    )

    mycursor = mydb.cursor()

    #Get values from constants.py
    slots = []
    slots = constants.slot #HV module slots
    channels = []
    channels = constants.channels #HV channels
    
    #Infinite loop to monitor HV and current
    
    #Connect to HV module
    hvModule = CAEN(b"90.147.203.174",b"admin",b"admin")
    handle = hvModule.connect()
    print("handle in main",handle)

    while True:
        try:
            print("---Alive counter:",alive,"---")
        
            #Get CAEN HV data
            for slot in range(len(slots)):
                for iCh, channel in enumerate(channels[slot]):
                    print("Slot",slots[slot],"channel",channel)
                    hvMon = hvModule.getParameter(handle,slots[slot],b"VMon",channel)
                    iMon = hvModule.getParameter(handle,slots[slot],b"IMon",channel)
                    hvSet = hvModule.getParameter(handle,slots[slot],b"V0Set",channel)
                    status = hvModule.getParameter(handle,slots[slot],b"Status",channel)
                    i0Set = hvModule.getParameter(handle,slots[slot],b"I0Set",channel)
                    name = hvModule.getChName(handle,slots[slot],channel)
                    hvEff = 0  #Just a test since PMTs have no effective HV

                    #insert into db every four iteractions of 15 seconds  (1 per minute)
                    if alive % 4 == 0:
                        print("Inserting data into db")
                        val = (slots[slot],channel,name,hvSet,hvMon,hvEff,iMon,status,i0Set)

                        hvMonitorQuery = "INSERT INTO CAEN (slot,channel,chName,hvSet,hvMon,hvEff,iMon,Status,i0Set) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" #sql query
                        mycursor.execute(hvMonitorQuery, val)

                        mydb.commit() #execute query
                        
            alive = alive+1
            time.sleep(15)

        except KeyboardInterrupt as e:
            hvModule.disconnect(handle)    
            print('Disconnecting from mainframe and stopping logger')
            exit()

if __name__ == "__main__":
    main()
