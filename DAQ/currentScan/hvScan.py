import constants #constants
from CAEN import CAEN

import numpy as np

import ctypes #for C++ function binding (CAEN HV library for example)
import pathlib

import mysql.connector #to connect to db to send the data

import ROOT #root CERN functions

import time #For functions such as sleep
import datetime #To get date, time and perform operations on them

import os #To create new folders and so on

import sys

import itertools

#Error function with different severity
def error(severity):
    if severity == 0:
        print("\nThis is debug\n")
    elif severity == 1:
        print("\nThis is a warning\n")
    elif severity == 2:
        print("\nThis is a serious error\n")    

#PT correction
def ptCorr(temp, press, hvEff):
  hvApp = hvEff*(constants.T0/temp)*(press/constants.p0)
  return hvApp

#Get last temp, press and humi from db
def getPT(mycursor):
    getLastEnv = ("SELECT temperature, pressure, humidity FROM envPar ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastEnv)

    lastEnv = mycursor.fetchall()
    return lastEnv

    #print("Done")

#main function, calling all helper functions
def main():

    print("---HV scan starting---")

    mydb = mysql.connector.connect( #db object on localhost
        host="localhost",
        user="root",
        password="Bello_figo97",
        database="labStrada"
    )
    mycursor = mydb.cursor()
    
    getLastRun = ("SELECT runNumber FROM currentScan ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastRun)

    lastRun = mycursor.fetchall()
    newRun = lastRun[0][0] + 1 #new run = last run + 1

    #insert new run in db
    run = [newRun] #A list is needed due to how mysql query works
    sendNewRun = "INSERT INTO currentScan (runNumber) VALUES (%s)" #sql query
    mycursor.execute(sendNewRun, run)
    mydb.commit()

    #Create folder to save the data locally
    newPath = "/home/luca/cernbox/arduinoCodes/labTurin/currentScans/scan_"+str(newRun) 
    if not os.path.exists(newPath):
        os.makedirs(newPath)

    #Get the configuration of the run -> append to lists defined in constants.py
    with open("/home/luca/cernbox/arduinoCodes/labTurin/configExample.txt") as configFile:
        scanPoints = configFile.readlines()
        scanPoints.pop(0)
        print(scanPoints)

        for point in scanPoints:
            asList = point.split("\t")
            length = len(asList)

            for i in range(length-2):
                constants.effHV.append(asList[i])
            constants.measTime.append(asList[length-2])
            constants.waitTime.append(asList[length-1].replace("\n", ""))

    print(constants.effHV)
    
    #Define CAEN HV module object (according to CAEN.py class)
    hvModule = CAEN(b"128.141.151.206",b"admin",b"admin")
    handle = hvModule.connect()
    #print("hanlde in main:",handle)

    slots = []
    slots = constants.slot
    channels = []
    channels = constants.channels
    
    #Calculate total number of channels to set proper HV values later on
    totChannels = sum([len(i) for i in channels])

    #General form to turn on channels
    for slot in range(len(slots)):
        #print("slot",slots[slot])
        #print(channels[slot])
        for channel in channels[slot]:
            hvModule.setParameter(handle,slots[slot],b"Pw",channel,1)            

    #Define general filename for DIP .root output file
    dipOut = "scan_"+str(newRun)+"_DIP_"
    caenOut = "scan_"+str(newRun)+"_CAEN_"

    #Go through the points of the scan
    hvPointCounter = 0

    chCounter = 0
    for i in range(int(len(constants.effHV)/totChannels)):
        
        print("Scanning point:",i+1)
        scanFol = "/home/luca/cernbox/arduinoCodes/labTurin/currentScans/scan_"+str(newRun)+"/HV_"+str(i+1)
        if not os.path.exists(scanFol):
            os.makedirs(scanFol)

        #Go in the folder 
        dipOut = dipOut+"HV"+str(i+1)+".root" 
        caenOut = caenOut+"HV"+str(i+1)+".root" 

        hHVmon = []
        hHVapp = []
        hHVeff = []
        hImon = []
        
        name = "test"

        for slot in range(len(slots)):
            for channel in channels[slot]:
                name = name+str(channel)
                elemHVmon = ROOT.TH1F(name+"HVmon_HV"+str(i+1),name+"HVmon_"+str(i+1),1000,0,1)
                elemHVmon.GetXaxis().SetCanExtend(True)
                elemHVapp = ROOT.TH1F(name+"HVapp_"+str(i+1),name+"HVapp_"+str(i+1),1000,0,1)
                elemHVapp.GetXaxis().SetCanExtend(True)
                elemHVeff = ROOT.TH1F(name+"HVeff_"+str(i+1),name+"HVeff_"+str(i+1),1000,0,1)
                elemHVeff.GetXaxis().SetCanExtend(True)
                elemImon = ROOT.TH1F(name+"Imon_"+str(i+1),name+"Imon_"+str(i+1),1000,0,1)
                elemImon.GetXaxis().SetCanExtend(True)
                hHVmon.append(elemHVmon)
                hHVapp.append(elemHVapp)
                hHVeff.append(elemHVeff)
                hImon.append(elemImon)

        lastEnv = getPT(mycursor)
        
        temperature = float(lastEnv[0][0])+273.15 #K
        pressure = float(lastEnv[0][1]) #mbar

        print(temperature)
        print(pressure)

        #Set corrected voltage to proper HV channel
        for slot in range(len(slots)):
            for channel in channels[slot]:
                print("Slot",slots[slot])
                print("Channel",channel)
                print("HVeff",constants.effHV[i+chCounter])
                hvApp = ptCorr(temperature, pressure, float(constants.effHV[i+chCounter]))
                hvModule.setParameter(handle,slots[slot],b"V0Set",channel,hvApp)
                print("HVapp",hvApp)
                if channel != channels[slot][-1]:
                    chCounter = chCounter+1
                
        #Set voltage on CAEN module
        #if handle != 0:
        #    print("CAEN HV module not connected")
        #    sys.exit("Exiting current scan"

        #Sleep for 2 seconds since, if channels are already on, it takes a bit of time
        #to change status from On to Ramp
        time.sleep(2)

        #Check if channels are still ramping up
        status = -1
        while status != 1:
            for slot in range(len(slots)):
                for channel in channels[slot]:
                    status = hvModule.getParameter(handle,slots[slot],b"Status",channel)
                    print("slot",slots[slot])
                    print("channel",channel)
                    print("status",status)

            print("Channels are ramping")
            time.sleep(2)

        print("Ramp up completed")
    
        #Wait for waiting time
        print("Waiting for waiting time")
        print(constants.waitTime[i])
        time.sleep(int(constants.waitTime[i]))
        print("Waiting time over")

        #Measure time 
        print("Starting measurement")
        t_end = time.time() + int(constants.measTime[i])

        while time.time() < t_end: #We are measuring
            chCounter = 0
            globalIndex = 0
            lastEnv = getPT(mycursor)
            temperature = lastEnv[0][0]+273.15
            pressure = lastEnv[0][1]
            print("temperature",temperature,"pressure",pressure)
           
            for slot in range(len(slots)):
                for channel in channels[slot]:
                    hvApp = ptCorr(temperature, pressure, float(constants.effHV[i+chCounter]))
                    hvModule.setParameter(handle,slots[slot],b"V0Set",channel,hvApp)
                    hvMon = hvModule.getParameter(handle,slots[slot],b"VMon",channel)
                    iMon = hvModule.getParameter(handle,slots[slot],b"IMon",channel)
                    hvSet = hvModule.getParameter(handle,slots[slot],b"V0Set",channel)
                    hHVmon[globalIndex].Fill(hvMon)
                    hImon[globalIndex].Fill(iMon)
                    hHVapp[globalIndex].Fill(hvSet)
                    print("Slot",slots[slot],"channel",channel,"hveff",constants.effHV[i+chCounter],"hvApp",hvApp)
                    globalIndex = globalIndex+1
                    if channel != channels[slot][-1]:
                        chCounter = chCounter+1
                
            time.sleep(constants.measureInt)
        
        print("Measuring time over, exiting from loop and changing HV")    


        os.chdir(scanFol)

        fOutDIP = ROOT.TFile(dipOut,"RECREATE")
        fOutCAEN = ROOT.TFile(caenOut,"RECREATE")
        
        fOutCAEN.cd()
        for j in range(totChannels):
            hvApp[j].Write("test"+str(j+1))
            hHVeff[j].Write("test"+str(j+1))
            hHVmon[j].Write("test"+str(j+1))
            hImon[j].Write("test"+str(j+1))
        fOutCAEN.Close()

        os.chdir("/home/luca/cernbox/arduinoCodes/labTurin")

        #Reset names and increase HV point counter
        #dipOut = newPath+"scan_"+str(newRun)+"_dip_"
        caenOut = "scan_"+str(newRun)+"_CAEN_"
        
    hvModule.disconnect(handle)
    print("Disconnected from module")

    #Placeholder for some debugging
    while True:
        #check if PT logging is active by checking at the time difference between current time and last entry in db
        getLastDate = ("SELECT date FROM envPar ORDER BY date DESC LIMIT 1")
        mycursor.execute(getLastDate)
        lastDate = mycursor.fetchall()
        print(type(lastDate[0][0]))

        delta = (datetime.datetime.now() - lastDate[0][0]).total_seconds()
        print(delta)

        if delta > 600:
            print("PT logging stopped more than 10 minutes ago!")
            print("Last PT saved is at:",str(lastDate[0][0]))
            print("Pausing current scan")
        
        else:
            print("All fine")


        time.sleep(100)
    

if __name__ == "__main__":
    main()