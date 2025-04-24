import os
import subprocess as sb
import time
import constants
from dotenv import dotenv_values
import mysql.connector #to connect to db to send the data
import ROOT #Root CERN functions
import sys
from datetime import datetime #To get date, time and perform operations on them
sys.path.insert(0, '/home/pcald32/labStrada/DAQ/currentScan') #import CAEN.py file from currentScan folder
from CAEN import CAEN

#PT correction
def ptCorr(temp, press, hvEff):
  hvApp = hvEff*(constants.T0/temp)*(press/constants.p0)
  return hvApp

#Get last temp, press and humi from db
def getPT(mycursor):
    getLastEnv = ("SELECT date, temperature, pressure FROM envPar ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastEnv)

    lastEnv = mycursor.fetchall()
    return lastEnv

#Check if HV channels are ramping up/down
def getStatus(hvModule,handle,totChannels,slots,channels):
    status = [-1] * totChannels
    #print(status)
    ramping = False

    chStatus = 0
    for slot in range(len(slots)):
        for channel in channels[slot]:
            status[chStatus] = hvModule.getParameter(handle,slots[slot],b"Status",channel)
            chStatus = chStatus+1

    #print(status)

    if status.count(1) != totChannels:
        ramping = True

    else:
        ramping = False

    return ramping

#If true -> print all debug information
debug = False

def main():

    print("----- Digitizer Scan starting -----")

    #Open .env file to get db credentials
    secrets = dotenv_values("/home/pcald32/labStrada/.env")

    #Connect to db
    mydb = mysql.connector.connect( #db object on localhost
        host=secrets["host"],
        user=secrets["user"],
        password=secrets["password"],
        database=secrets["database"]
    )

    mycursor = mydb.cursor()

    #Possibly send run info to db
    ##
    ##
    ##

    #Get values from constants.py
    effHV = constants.effHV #Effective high voltage values
    slots = []
    slots = constants.slot #HV module slots
    channels = []
    channels = constants.channels #HV channels
    chName = []
    chName = constants.names #Channels name
    trigNum = []

    #Calculate total number of channels to set proper HV values later on
    totChannels = sum([len(i) for i in channels])

    #Get the configuration of the run from the config file
    with open("/home/pcald32/labStrada/config/configEffScan.txt") as configFile:
        scanPoints = configFile.readlines()
        scanPoints.pop(0)
        
        if debug:
            print(scanPoints)

        for point in scanPoints:
            if debug:
                print(point)
            
            asList = point.split("\t")
            
            if debug:
                print(asList)
            
            length = len(asList)
            
            if debug:
                print(length)

            iCh = 0
            for slot in range(len(slots)):
                for channel in enumerate(channels[slot]):
                    effHV[slot].append(asList[iCh])
                    iCh = iCh+1

            constants.measTime.append(asList[length-3])
            constants.waitTime.append(asList[length-2])
            trigNum.append(int(asList[length-1].replace("\n", "")))

    print("Connecting to CAEN HV module")
    hvModule = CAEN(b"90.147.203.174",b"admin",b"admin")

    #Connect to CAEN HV module
    handle = hvModule.connect()
    for slot in range(len(slots)):
        for iCh, channel in enumerate(channels[slot]):
            hvModule.setParameter(handle,slots[slot],b"Pw",channel,1)
            hvModule.setChName(handle,slots[slot],channel,chName[slot][iCh])

    #Create folder to save the data locally
    newRun = 1
    newPath = "/home/pcald32/runs/digitizer/scan_"+str(newRun) 
    if not os.path.exists(newPath):
        os.makedirs(newPath)

    #Loop over HV points
    for i in range(int(len(constants.measTime))):

        print("Scanning HV point: ", i+1)

        print("Number of triggers: ",trigNum[i])

        #Create HV1, HV2,... folders in the run folder
        scanFol = "/home/pcald32/runs/digitizer/scan_"+str(newRun)+"/HV_"+str(i+1)+"/"
        if not os.path.exists(scanFol):
            os.makedirs(scanFol)

        #Go in the folder and create root files
        #Define general filename for DIP .root output file
        dipOut = scanFol+"scan_"+str(newRun)+"_DIP_HV"+str(i+1)+".root"
        caenOut = scanFol+"scan_"+str(newRun)+"_CAEN_HV"+str(i+1)+".root"

        #os.chdir(scanFol)

        fOutDIP = ROOT.TFile(dipOut,"RECREATE")
        fOutCAEN = ROOT.TFile(caenOut,"RECREATE")

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

        #Get last PT values to apply initial correction to HV
        mydb.cmd_refresh(1)
        lastEnv = getPT(mycursor)
        lastDate = lastEnv[0][0]
        delta = (datetime.now() - lastDate).total_seconds() #Calculate difference between now and last measurement in the db

        while delta > 1200: #1200 s = logger stopped for more than 20 minutes
            mydb.cmd_refresh(1)
            lastEnv = getPT(mycursor)
            lastDate = lastEnv[0][0]
            delta = (datetime.now() - lastDate).total_seconds()
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

        #Sleep for 2 seconds since, if channels are already on, it takes a bit of time to change status from ON to Ramp UP/DOWN
        time.sleep(2)

        printedMessage = False #boolean to check if "channels are ramping" message has already been printed
        #Check if the channels are ramping
        while getStatus(hvModule,handle,totChannels,slots,channels) == True:
            if printedMessage == False: #Print message only once
                printedMessage = True
                print("Channels are ramping")
            
            time.sleep(2) #sleep for two seconds to relax a bit, not needed but ok, it can be used

        print("Ramping completed")

        #Disconnect from HV mainframe during waiting time
        hvModule.disconnect(handle) 
        
        print("Waiting for waiting time: ",constants.waitTime[i],"s")
        time.sleep(int(constants.waitTime[i]))
        print("Waiting time over")

        #Reconnect to mainframe after waiting time
        hvModule.connect()
        time.sleep(2)

        ###########################
        #                         #
        # Launch wawedump program #
        #                         #
        ###########################

        cmd = ['/home/pcald32/wavedump-3.10.6/src/./wavedump', '/home/pcald32/wavedump-3.10.6/WaveDumpConfig.txt', str(trigNum[i]),scanFol]
        pWaveDump = sb.Popen(cmd)

        stampa = True
        
        #While wavedump is still taking data, do the HV scan and correction
        #If the wavedump has finished running, it will return a not None code and 
        #the while loop will be interrupted, the histograms will be saved and the code will move to the next HV point
        while pWaveDump.poll() is None:
            
            if stampa:
                print("Wavedump taking data...")
                stampa = False

            globalIndex = 0
            
            lastEnv = getPT(mycursor)
            lastDate = lastEnv[0][0]
            delta = (datetime.now() - lastDate).total_seconds() #Calculate difference between now and last measurement in the db

            while delta > 1200:
                t_end = t_end + 3 #this is needed because the way to measure residual time is to compute t_end before the start of measuring time
                #but even if the PT logging is stopped, the time still passes. In this way we extend the end of run by 3 seconds, which is the waiting
                #time at the end of (while delta > 1200). This is precise to ~0.1 s, it can be improved by measuring how long the loop is but for the moment
                #it is good enough
                mydb.cmd_refresh(1)
                lastEnv = getPT(mycursor)
                lastDate = lastEnv[0][0]
                delta = (datetime.now() - lastDate).total_seconds()
                print("PT logging stopped more than 10 minutes ago!")
                print("Last PT saved is at:",str(lastDate))
                print("Pausing current scan until PT resumes")  
                time.sleep(3)

            temperature = lastEnv[0][1]+273.15
            pressure = lastEnv[0][2]

            hTemp.Fill(lastEnv[0][1]) #Fill temperature histo
            hPress.Fill(lastEnv[0][2]) #Fill pressure histo
            #hHumi.Fill(lastEnv[0][3]) #Fill humidity histo
            #hFlow.Fill(lastEnv[0][4]) #Fill flow histo
        
            for slot in range(len(slots)):
                for iCh, channel in enumerate(channels[slot]):
                    #print("i",i)
                    #print("slot",slot)
                    #print("iCh",iCh)
                    #print("channel",channel)
                    hvApp = ptCorr(temperature, pressure, float(effHV[slot][iCh+(i*len(channels[slot]))]))
                    hvModule.setParameter(handle,slots[slot],b"V0Set",channel,hvApp)
                    
                    hvMon = hvModule.getParameter(handle,slots[slot],b"VMon",channel)
                    iMon = hvModule.getParameter(handle,slots[slot],b"IMon",channel)
                    hvSet = hvModule.getParameter(handle,slots[slot],b"V0Set",channel)
                    
                    hHVeff[globalIndex].Fill(float(effHV[slot][iCh+(i*len(channels[slot]))]))
                    hHVmon[globalIndex].Fill(hvMon)
                    hImon[globalIndex].Fill(iMon)
                    hHVapp[globalIndex].Fill(hvSet)
                    #print("Slot",slots[slot],"channel",channel,"hveff",effHV[slot][iCh+(i*len(channels[slot]))],"hvApp",hvApp)
                    globalIndex = globalIndex+1

            time.sleep(2)

        print("Desired trigger number reached")

        print("Saving histograms in root file")

        fOutCAEN.cd()
        ch = 0
        for slot in range(len(slots)):
            for iCh, channel in enumerate(channels[slot]):
                hHVapp[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_app_"+str(i+1))
                hHVeff[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_eff_"+str(i+1))
                hHVmon[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_mon_"+str(i+1))
                hImon[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_I_mon_"+str(i+1))
                ch=ch+1

        fOutDIP.cd()
        hTemp.Write("Temperature_HV_"+str(i+1))
        hPress.Write("Pressure_HV_"+str(i+1))
        hHumi.Write("Humidity_HV_"+str(i+1))

        fOutCAEN.Close()
        fOutDIP.Close()

        print("Moving to the next HV point")

    print("Scan is over, disconnecting from HV mainframe")
    #Disconnect from HV mainframe during waiting time
    hvModule.disconnect(handle) 

if __name__ == "__main__":
    main()