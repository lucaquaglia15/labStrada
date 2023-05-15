#import constants #constants
from VME import VME #Python version of CAEN HV wrapper library
from TDC import TDC #Functions specific to the V488A TDC module
import numpy as np #numpy
import ctypes #for C++ function binding (CAEN HV library for example)
import pathlib #for library paths (to use C++ libraries in python)
import mysql.connector #to connect to db to send the data
import ROOT #Root CERN functions
import time #For functions such as sleep
import datetime #To get date, time and perform operations on them
import os #To create new folders and so on
import sys #To perform system operation
import array
import constants
sys.path.insert(0, '/home/pcald32/labStrada/DAQ/currentScan') #import CAEN.py file from currentScan folder
from CAEN import CAEN

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

debug = False

#main function for current scan
def main():

    print("---Efficiency scan starting---")

    mydb = mysql.connector.connect( #db object
        host="localhost",
        user="root",
        password="pcald32",
        database="labStrada"
    )
    mycursor = mydb.cursor()
    
    getLastRun = ("SELECT runNumber FROM efficiencyScan ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastRun)

    lastRun = mycursor.fetchall()
    newRun = lastRun[0][0] + 1 #new run = last run + 1

    #insert new run in db
    run = [newRun] #A list is needed due to how mysql query works
    sendNewRun = "INSERT INTO efficiencyScan (runNumber) VALUES (%s)"
    mycursor.execute(sendNewRun, run)
    mydb.commit()

    #Create folder to save the data locally
    newPath = "/home/pcald32/runs/efficiencyScans/scan_"+str(newRun) 
    if not os.path.exists(newPath):
        os.makedirs(newPath)
        os.chdir(newPath)
        fOutDAQ = ROOT.TFile("test.root","RECREATE")
    
    #Define arrays to fill for tree branches
    size = array.array( 'l', [ 0 ] )
    aChannels = array.array('i')
    aTimes = array.array('f')

    #Create TTree and branch it to save DAQ data
    treeDAQ = ROOT.TTree("treeDAQ","Data from TDCs")
    treeDAQ.Branch('size', size, 'size/I')
    treeDAQ.Branch("channels",aChannels,'channels[size]/I') 
    treeDAQ.Branch("times",aTimes,'times[size]/F')
    
    print("Getting configuration file for V488A TDC")
    
    #Get values from constants.py
    effHV = constants.effHV #effective high voltage values
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

    BA = [] #TDC base addresses
    lowTh = [] #TDC low thresholds
    highTh = [] #TDC high thresholds
    window = [] #TDC time window
    enablech = [] #TDC enable channels
    IRQ = [] #TDC IRQ level e status

    with open("/home/pcald32/labStrada/config/TDCconfig.txt") as TDCconfig:
        TDCparam = TDCconfig.readlines()
        TDCparam.pop(0)
        TDCparam.pop(0)

        if debug:
            print(TDCparam)
       
        for tdc in TDCparam:
            asList = tdc.split("\t")
            BA.append(int(asList[1],16))
            lowTh.append(int(asList[2],16))
            highTh.append(int(asList[3],16))
            window.append(int(asList[4],16))
            enablech.append(int(asList[5],16))
            IRQ.append(int(asList[6],16))

    #connect to VME bridge
    print("connecting to VME bridge")
    VMEbridge = VME(1,0,0)
    handle = VMEbridge.connect()

    print("Connecting to CAEN HV module")
    hvModule = CAEN(b"90.147.203.174",b"admin",b"admin")

    #start pulser for VETO
    print("starting pulser")
    VMEbridge.configPulser(handle,0,1,40000000,0,0,0,0)
    VMEbridge.setOutputConf(handle,0,0,0,6)
    VMEbridge.startPulser(handle,0)

    #configure TDCs
    print("\n configuring TDCs \n")
    
    TDCs = [] #empty list to define one TDC object for every TDC used in the DAQ
    
    for tdc in range(len(BA)):
        TDCs.append(TDC(BA[tdc],lowTh[tdc],highTh[tdc],window[tdc],enablech[tdc],IRQ[tdc]))
    
    for tdc in range(len(BA)):
        TDCs[tdc].resetModule(VMEbridge,handle)
        TDCs[tdc].setLowThr(VMEbridge,handle)
        TDCs[tdc].setHighThr(VMEbridge,handle)
        TDCs[tdc].setTimeWindow(VMEbridge,handle)
        TDCs[tdc].accessIRQregister(VMEbridge,handle,1)
        TDCs[tdc].accessIRQregister(VMEbridge,handle,0)
        TDCs[tdc].accessControlRegister(VMEbridge,handle,1)
        TDCs[tdc].accessControlRegister(VMEbridge,handle,0)
    
    print("\n Configuration done, starting scan \n")
    
    VMEbridge.resetScalerCount(handle)
    
    print("\n Scaler counts:",VMEbridge.readRegister(handle,0x1D))

    VMEbridge.confScaler(handle,0,0,1,0,0)
    VMEbridge.enableScalerGate(handle)

    VMEbridge.enableIRQ(handle,111)

    """
    handle = hvModule.connect()
    for slot in range(len(slots)):
        for iCh, channel in enumerate(channels[slot]):
            hvModule.setParameter(handle,slots[slot],b"Pw",channel,1)
            hvModule.setChName(handle,slots[slot],channel,chName[slot][iCh])

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
    """

    VMEbridge.stopPulser(handle,0)

    if hex(VMEbridge.checkIRQ(handle)) == hex(0x0):
        waitingIRQ = True
        print("Waiting for IRQ")
    
    while waitingIRQ:

        if VMEbridge.readRegister(handle,0x1D)>=int(hex(trigNum[0]),16):
            print("Desidered trigger number reached, moving to the next HV point")
            print("Numero di trigger impostati: ",int(hex(trigNum[0]),16))
            print("Numero di trigger calcolati: ",int(VMEbridge.readRegister(handle,0x1D)))
            fOutDAQ.cd()
            treeDAQ.Write()
            fOutDAQ.Close()
            break
        
        else:
            VMEbridge.stopPulser(handle,0)
            IRQlevel = hex(VMEbridge.checkIRQ(handle))
            event = []

            while IRQlevel != hex(0x0):
                VMEbridge.disableIRQ(handle,111)

                VMEbridge.startPulser(handle,0)
                IRQvector = VMEbridge.iackCycle(handle,int(IRQlevel,16),0x01)
                print("IRQ ricevuta")
                print("IRQvector: ",IRQvector) 
                print("IRQlevel: ",IRQlevel)
                header = []
                
                whichTDC = -1
                
                if IRQvector == hex(0x1):
                    whichTDC = 0
                elif IRQvector == hex(0x2):
                    whichTDC = 1
                elif IRQvector == hex(0x3):
                    whichTDC = 2

                header = TDCs[whichTDC].readOutputBuffer(VMEbridge,handle)
                #time.sleep(2)
                print("\n", "Header 0:",header[0],"\n")
                
                for ch in range(header[0]):
                    print("ch", ch)
                    event.append(TDCs[whichTDC].readOutputBuffer(VMEbridge,handle))
                    #print("\ntime:",TDCs[whichTDC].converter(TDCs[whichTDC].readOutputBuffer(VMEbridge,handle)))
                #time.sleep(2)

                print("\n",event,"\n")

                IRQlevel = hex(VMEbridge.checkIRQ(handle))
                print("IRQ level a fine loop ",IRQlevel)
                
                if IRQlevel == hex(0x0):
                    print(type(event), event)
                    lChannels,lTimes = map(list,zip(*event))
                    print(lChannels, lTimes)
                    
                    size[0] = len(lChannels)
                    
                    #Fill tree
                    for i in range(len(lChannels)):
                        aChannels.append(lChannels[i])
                        aTimes.append(lTimes[i])
                    
                    if debug:
                        print("memory address of a",hex(id(a)))
                        print("channels as array before: ",aChannels, type(aChannels))
                        print("times as array before: ",aTimes, type(aTimes))
                    
                    treeDAQ.SetBranchAddress('channels',aChannels)
                    treeDAQ.SetBranchAddress('times',aTimes)

                    treeDAQ.Fill()
                    
                    del aChannels[:]
                    del aTimes[:]
                    del event[:]

                    print("\n\n scaler counts nel loop :", VMEbridge.readRegister(handle,0x1D),"\n\n")

                    if VMEbridge.readRegister(handle,0x1D)>=int(hex(trigNum[0]),16):
                        print("Desidered trigger number reached, moving to the next HV point")
                        print("Numero di trigger impostati: ",int(hex(trigNum[0]),16))
                        print("Numero di trigger calcolati: ",int(VMEbridge.readRegister(handle,0x1D)))
                        fOutDAQ.cd()
                        treeDAQ.Write()
                        fOutDAQ.Close()
                        break

                    VMEbridge.enableIRQ(handle,111)
                    #event.clear()

                    time.sleep(1)


if __name__ == "__main__":
    main()
