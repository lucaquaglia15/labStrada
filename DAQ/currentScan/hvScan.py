import constants #constants
from CAEN import CAEN #Python version of CAEN HV wrapper library
import numpy as np #numpy
import ctypes #for C++ function binding (CAEN HV library for example)
import pathlib #for library paths (to use C++ libraries in python)
import mysql.connector #to connect to db to send the data
import ROOT #Root CERN functions
import time #For functions such as sleep
import datetime #To get date, time and perform operations on them
import os #To create new folders and so on
import sys #To perform system operation

debug = False

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
    getLastEnv = ("SELECT date, temperature, pressure, humidity FROM envPar ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastEnv)

    lastEnv = mycursor.fetchall()
    return lastEnv

#Check if channels are ramping up/down
def getStatus(hvModule,handle,totChannels,slots,channels):
    status = [-1] * totChannels
    print(status)
    ramping = False

    chStatus = 0
    for slot in range(len(slots)):
        for channel in channels[slot]:
            status[chStatus] = hvModule.getParameter(handle,slots[slot],b"Status",channel)
            chStatus = chStatus+1

    print(status)

    if status.count(1) != totChannels:
        ramping = True

    else:
        ramping = False

    return ramping

#main function for current scan
def main():

    print("---HV scan starting---")

    mydb = mysql.connector.connect( #db object
        host="localhost",
        user="root",
        password="pcald32",
        database="labStrada"
    )
    mycursor = mydb.cursor()

    #Check the mixture that is being flushed and send the data to db
    
    getLastRun = ("SELECT runNumber FROM currentScan ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastRun)

    lastRun = mycursor.fetchall()
    newRun = lastRun[0][0] + 1 #new run = last run + 1

    #insert new run in db
    run = [newRun] #A list is needed due to how mysql query works
    sendNewRun = "INSERT INTO currentScan (runNumber) VALUES (%s)"
    mycursor.execute(sendNewRun, run)
    mydb.commit()

    #runConfig = [totChannels,]
    #sendRunConfig = "INSERT INTO .. VALUES (%s)"

    #Create folder to save the data locally
    newPath = "/home/pcald32/runs/currentScans/scan_"+str(newRun) 
    if not os.path.exists(newPath):
        os.makedirs(newPath)

    #Get values from constants.py
    effHV = constants.effHV #effective high voltage values
    slots = []
    slots = constants.slot #HV module slots
    channels = []
    channels = constants.channels #HV channels
    chName = []
    chName = constants.names #Channels name
    
    #Calculate total number of channels to set proper HV values later on
    totChannels = sum([len(i) for i in channels])

    #Get the configuration of the run from the config file
    with open("/home/pcald32/labStrada/config/configExample.txt") as configFile:
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
    
    #Define CAEN HV module object (according to CAEN.py class) and try to connect to it
    hvModule = CAEN(b"90.147.203.174",b"admin",b"admin")
    handle = hvModule.connect()

    #Set channel name and switch HV on
    for slot in range(len(slots)):
        for iCh, channel in enumerate(channels[slot]):
            hvModule.setParameter(handle,slots[slot],b"Pw",channel,1)
            hvModule.setChName(handle,slots[slot],channel,chName[slot][iCh])            

    #Define general filename for DIP .root output file
    dipOut = "scan_"+str(newRun)+"_DIP_"
    caenOut = "scan_"+str(newRun)+"_CAEN_"

    #Go through the points of the scan
    for i in range(int(len(constants.measTime))):
        
        if debug:
            print(i)
    
        print("Scanning point:",i+1)
        scanFol = "/home/pcald32/runs/currentScans/scan_"+str(newRun)+"/HV_"+str(i+1)
        if not os.path.exists(scanFol):
            os.makedirs(scanFol)

        #Go in the folder 
        dipOut = dipOut+"HV"+str(i+1)+".root" 
        caenOut = caenOut+"HV"+str(i+1)+".root" 

        #Declare list of histograms to save CAEN values
        hHVmon = []
        hHVapp = []
        hHVeff = []
        hImon = []

        #Append CAEN histograms to lists declared earlier
        for slot in range(len(slots)):
            for iCh, channel in enumerate(channels[slot]):
                elemHVmon = ROOT.TH1F(str(chName[slot][iCh].decode('utf-8'))+"_HVmon_HV"+str(i+1),str(chName[slot][iCh])+"_HVmon_"+str(i+1),1000,0,1)
                elemHVmon.GetXaxis().SetCanExtend(True)
                elemHVapp = ROOT.TH1F(str(chName[slot][iCh].decode('utf-8'))+"_HVapp_"+str(i+1),str(chName[slot][iCh])+"_HVapp_"+str(i+1),1000,0,1)
                elemHVapp.GetXaxis().SetCanExtend(True)
                elemHVeff = ROOT.TH1F(str(chName[slot][iCh].decode('utf-8'))+"_HVeff_"+str(i+1),str(chName[slot][iCh])+"_HVeff_"+str(i+1),1000,0,1)
                elemHVeff.GetXaxis().SetCanExtend(True)
                elemImon = ROOT.TH1F(str(chName[slot][iCh].decode('utf-8'))+"_Imon_"+str(i+1),str(chName[slot][iCh])+"_Imon_"+str(i+1),1000,0,1)
                elemImon.GetXaxis().SetCanExtend(True)
                hHVmon.append(elemHVmon)
                hHVapp.append(elemHVapp)
                hHVeff.append(elemHVeff)
                hImon.append(elemImon)

        #Declare histograms to save DIP values
        hTemp = ROOT.TH1F("Temperature_HV"+str(i+1),"Temperature_HV_"+str(i+1),1000,0,1)
        hTemp.GetXaxis().SetCanExtend(True)
        hPress = ROOT.TH1F("Pressure_HV"+str(i+1),"Pressure_HV_"+str(i+1),1000,0,1)
        hPress.GetXaxis().SetCanExtend(True)
        hHumi = ROOT.TH1F("Humidity_HV"+str(i+1),"Humidity_HV"+str(i+1),1000,0,1)
        hHumi.GetXaxis().SetCanExtend(True)
        hFlow = ROOT.TH1F("Flow_HV"+str(i+1),"Flow_HV"+str(i+1),1000,0,1)
        hFlow.GetXaxis().SetCanExtend(True)

        #Get last PT values to apply initial correction to HV
        mydb.cmd_refresh(1)
        lastEnv = getPT(mycursor)
        lastDate = lastEnv[0][0]
        delta = (datetime.datetime.now() - lastDate).total_seconds() #Calculate difference between now and last measurement in the db

        while delta > 1200: #1200 s = logger stopped for more than 20 minutes
            mydb.cmd_refresh(1)
            lastEnv = getPT(mycursor)
            lastDate = lastEnv[0][0]
            delta = (datetime.datetime.now() - lastDate).total_seconds()
            print("PT logging stopped more than 10 minutes ago!")
            print("Last PT saved is at:",str(lastDate))
            print("Pausing current scan until PT logging resumes")  
            time.sleep(3)

        temperature = float(lastEnv[0][1])+273.15 #K
        pressure = float(lastEnv[0][2]) #mbar

        #Set corrected voltage to proper HV channel and then wait that voltages reaches desired value
        for slot in range(len(slots)):
            for iCh, channel in enumerate(channels[slot]):
                print("Slot",slots[slot],"channel",channel,"HVeff",effHV[slot][iCh+(i*len(channels[slot]))])
                hvApp = ptCorr(temperature, pressure, float(effHV[slot][iCh+(i*len(channels[slot]))]))
                hvModule.setParameter(handle,slots[slot],b"V0Set",channel,hvApp)
                print("HVapp",hvApp)

        #Check if connection to HV module is active
        if handle.value != 0:
            print("CAEN HV module not connected")
            hvModule.disconnect(handle)
            sys.exit("Exiting current scan")

        #Sleep for 2 seconds since, if channels are already on, it takes a bit of time to change status from ON to Ramp UP/DOWN
        time.sleep(2)

        #Check if the channels are ramping
        while getStatus(hvModule,handle,totChannels,slots,channels) == True:
            print("Channels are ramping")
            time.sleep(2)

        print("Ramping completed")

        hvModule.disconnect(handle)
    
        #Wait for waiting time
        print("Waiting for waiting time")
        print(constants.waitTime[i],"s")
        time.sleep(int(constants.waitTime[i]))
        print("Waiting time over")

        hvModule.connect()
        time.sleep(2)

        #Start measuring
        print("Starting measurement")
        t_end = time.time() + int(constants.measTime[i])
        
        while time.time() < t_end: #We are measuring
            mydb.cmd_refresh(1) #refresh db to get last entry
            globalIndex = 0
            
            lastEnv = getPT(mycursor)
            lastDate = lastEnv[0][0]
            delta = (datetime.datetime.now() - lastDate).total_seconds() #Calculate difference between now and last measurement in the db

            while delta > 1200:
                t_end = t_end + 3 #this is needed because the way to measure residual time is to compute t_end before the start of measuring time
                #but even if the PT logging is stopped, the time still passes. In this way we extend the end of run by 3 seconds, which is the waiting
                #time at the end of (while delta > 1200). This is precise to ~0.1 s, it can be improved by measuring how long the loop is but for the moment
                #it is good enough
                mydb.cmd_refresh(1)
                lastEnv = getPT(mycursor)
                lastDate = lastEnv[0][0]
                delta = (datetime.datetime.now() - lastDate).total_seconds()
                print("PT logging stopped more than 10 minutes ago!")
                print("Last PT saved is at:",str(lastDate))
                print("Pausing current scan until PT resumes")  
                time.sleep(3)

            temperature = lastEnv[0][1]+273.15
            pressure = lastEnv[0][2]
            print("temperature",temperature,"pressure",pressure)

            hTemp.Fill(lastEnv[0][1]) #Fill temperature histo
            hPress.Fill(lastEnv[0][2]) #Fill pressure histo
            hHumi.Fill(lastEnv[0][3]) #Fill humidity histo
            #hFlow.Fill(lastEnv[0][4]) #Fill flow histo
           
            for slot in range(len(slots)):
                for iCh, channel in enumerate(channels[slot]):
                    hvApp = ptCorr(temperature, pressure, float(effHV[slot][iCh+(i*len(channels[slot]))]))
                    hvModule.setParameter(handle,slots[slot],b"V0Set",channel,hvApp)
                    
                    hvMon = hvModule.getParameter(handle,slots[slot],b"VMon",channel)
                    iMon = hvModule.getParameter(handle,slots[slot],b"IMon",channel)
                    hvSet = hvModule.getParameter(handle,slots[slot],b"V0Set",channel)
                    
                    hHVeff[globalIndex].Fill(float(effHV[slot][iCh+(i*len(channels[slot]))]))
                    hHVmon[globalIndex].Fill(hvMon)
                    hImon[globalIndex].Fill(iMon)
                    hHVapp[globalIndex].Fill(hvSet)
                    print("Slot",slots[slot],"channel",channel,"hveff",effHV[slot][iCh+(i*len(channels[slot]))],"hvApp",hvApp)
                    globalIndex = globalIndex+1
                
            time.sleep(constants.measureInt)
        
        print("Measuring time over, exiting from loop and changing HV")    

        os.chdir(scanFol)

        fOutDIP = ROOT.TFile(dipOut,"RECREATE")
        fOutCAEN = ROOT.TFile(caenOut,"RECREATE")
        
        fOutCAEN.cd()

        ch = 0
        for slot in range(len(slots)):
            for iCh, channel in enumerate(channels[slot]):
                hHVapp[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_app_"+str(i+1))
                hHVeff[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_eff_"+str(i+1))
                hHVmon[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_mon_"+str(i+1))
                hImon[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_I_mon_"+str(i+1))
                ch=ch+1
        fOutCAEN.Close()

        fOutDIP.cd()
        hTemp.Write("Temperature_HV_"+str(i+1))
        hPress.Write("Pressure_HV_"+str(i+1))
        hHumi.Write("Humidity_HV_"+str(i+1))
        hFlow.Write("Flow_HV_"+str(i+1))
        fOutDIP.Close()

        os.chdir("/home/pcald32/labStrada/DAQ/currentScan")

        #Reset names and increase HV point counter
        dipOut = "scan_"+str(newRun)+"_DIP_"
        caenOut = "scan_"+str(newRun)+"_CAEN_"
      
    print("HV scan ended, switching off detectors")
    for slot in range(len(slots)):
        for channel in channels[slot]:
            hvModule.setParameter(handle,slots[slot],b"V0Set",channel,0)
            hvModule.setParameter(handle,slots[slot],b"Pw",channel,0)

    hvModule.disconnect(handle)
    print("Disconnected from HV module")
    
if __name__ == "__main__":
    main()
