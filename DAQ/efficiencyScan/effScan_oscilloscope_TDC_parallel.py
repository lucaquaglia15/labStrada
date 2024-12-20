from ast import arg
from typing import NewType
from VME import VME #Python version of CAEN HV wrapper library
from TDC import TDC #Functions specific to the V488A TDC module
import numpy as np #numpy
import ctypes #for C++ function binding (CAEN HV library for example)
import pathlib #for library paths (to use C++ libraries in python)
import pandas
import mysql.connector #to connect to db to send the data
import ROOT #Root CERN functions
import time #For functions such as sleep
from datetime import datetime #To get date, time and perform operations on them
import os #To create new folders and so on
import sys #To perform system operation
import array
import constants #Constant parameters for run configuration
import TeledyneLeCroyPy #Control oscilloscope
from multiprocessing import Process #To parallelize processes (PT corr mainly)
from dotenv import dotenv_values
sys.path.insert(0, '/home/pcald32/labStrada/DAQ/currentScan') #import CAEN.py file from currentScan folder
from CAEN import CAEN

#Set final voltage to RPCs at the end of scan
def switchOff(handle,hvModule,slots,channels,hvApp):
    print("Setting end-of-run high voltage: ", hvApp)
    
    globalIndex = 0
    
    for slot in range(len(slots)):
        for iCh, channel in enumerate(channels[slot]):
            hvModule.setParameter(handle,slots[slot],b"V0Set",channel,hvApp)
            if hvApp == 0: #If set hv = 0 -> swtich off the channel
                hvModule.setParameter(handle,slots[slot],b"Pw",channel,0)

            globalIndex = globalIndex+1

#PT correction
def ptCorr(temp, press, hvEff):
  hvApp = hvEff*(constants.T0/temp)*(press/constants.p0)
  return hvApp

#Get last temp, press and humi from db
def getPT(mycursor):
    #getLastEnv = ("SELECT date, temperature, pressure, humidity FROM envPar ORDER BY date DESC LIMIT 1")
    getLastEnv = ("SELECT date, temperature, pressure FROM envPar ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastEnv)

    lastEnv = mycursor.fetchall()
    return lastEnv

#Function to apply the PT correction and write the data to the root file
#do this in parallel with the rest of the DAQ
def applyPTCorr(mydb,mycursor,hTemp,hPress,hHumi,hFlow,hvModule,handle,slots,channels,
                hHVeff,hHVapp,hHVmon,hImon,effHV,i):
    
    while True:
        mydb.connect()
        
        print("\n HV correction process in parallel \n")
        print("Memory address of hTemp in pt corr function: ", id(hTemp))
        print("Memory address of hPress in pt corr function: ", id(hPress))
        print("Memory address of hHumi in pt corr function: ", id(hHumi))
        print("Memory address of hFlow in pt corr function: ", id(hFlow))
        print("Memory address of hHVeff in pt corr function: ", id(hHVeff))
        print("Memory address of hHVapp in pt corr function: ", id(hHVapp))
        print("Memory address of hHVmon in pt corr function: ", id(hHVmon))
        print("Memory address of hImon in pt corr function: ", id(hImon))
        print(hHVeff)

        mydb.cmd_refresh(1) #refresh db to get last entry
            
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
        print("In parallel function, entries of hTemp after filling: ",hTemp.GetEntries())
        #hHumi.Fill(lastEnv[0][3]) #Fill humidity histo
        #hFlow.Fill(lastEnv[0][4]) #Fill flow histo
        
        for slot in range(len(slots)):
            for iCh, channel in enumerate(channels[slot]):
                print("i",i,"slot",slot,"iCh",iCh,"channel",channel)
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
        
        mydb.close()
        
        time.sleep(10)

#Write oscilloscope data
def writeScope(scope,waveOut,channels): #scope = oscilloscope object, waveOut = output .txt file
                                        #channels = list of active channels (defined in main functuon)
    scope.wait_for_single_trigger() #Wait for a trigger, it will be delayed accordingly 
                                    #(Accordingly = more than for the TDC modules, to allow for IRQ creation)
                                    #To be checked
    data = {} #Dictionary
    
    for n_channel in channels: #Loop to get the data from active channels
        data[n_channel] = scope.get_waveform(n_channel=n_channel)

    wf = []
    for n_channel in data:
        for i,_ in enumerate(data[n_channel]['waveforms']):
            df = pandas.DataFrame(_)
            df['n_segment'] = i
            df['n_channel'] = n_channel
            wf.append(df)
    
    #wf = pandas.concat(wf) #original
    wf = pandas.concat(wf, axis=1) #In theory this should concatenate the dataframes according to the initial "axis"
                                   #which is the common timebase to all channels, as reported in:
                                   #https://www.geeksforgeeks.org/pandas-concat-function-in-python/ but it has to be
                                   #checked with the data
    #Write trigger number and df to output .txt file
    wf.to_csv(waveOut, sep='\t', index=False) #write event
    waveOut.write("\n") #New line at the end of the event
    waveOut.flush() #Write out to the txt file


#Check if channels are ramping up/down
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

#main function for efficiency scan
debug = False

def main():

    print("---Efficiency scan starting---")

    secrets = dotenv_values("/home/pcald32/labStrada/.env") #load passwords and db data

    arguments = sys.argv  #Get command line arguments (#0 =  mixture, #1 = scan type, #3 = comments, #4 = HV to set at the end of the scan)
    
    while len(arguments) < 5: #Check if size of arguments is smaller than 3 (it means that some argument is missing by mistake)
        #add "" until size 5 is reached, some information on the run will be lost but it doesn't matter
        arguments.append("")

    mydb = mysql.connector.connect( #db object on localhost
        host=secrets["host"],
        user=secrets["user"],
        password=secrets["password"],
        database=secrets["database"]
    )

    mycursor = mydb.cursor()
    
    getLastRun = ("SELECT runNumber FROM efficiencyScan ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastRun)

    lastRun = mycursor.fetchall()
    newRun = lastRun[0][0] + 1 #new run = last run + 1

    #insert new run in db
    run = [newRun,arguments[1],arguments[2],arguments[3]] #A list is needed due to how mysql query works
    sendNewRun = "INSERT INTO efficiencyScan (runNumber,mixture,runType,comments) VALUES (%s,%s,%s,%s)"
    mycursor.execute(sendNewRun, run)
    mydb.commit()

    #Create folder to save the data locally
    newPath = "/home/pcald32/runs/efficiencyScans/scan_"+str(newRun) 
    if not os.path.exists(newPath):
        os.makedirs(newPath)
    
    #Define arrays to fill for tree branches
    eventNumber = array.array( 'l', [ 0 ] )
    size = array.array( 'l', [ 0 ] )
    aChannels = array.array('i')
    aTimes = array.array('f')
 
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
 
    TDCs = [] #empty list to define one TDC object for every TDC used in the DAQ
    
    for tdc in range(len(BA)):
        TDCs.append(TDC(BA[tdc],lowTh[tdc],highTh[tdc],window[tdc],enablech[tdc],IRQ[tdc]))
    
    time.sleep(1)
    
    #Connect to CAEN HV module
    handle = hvModule.connect()
    for slot in range(len(slots)):
        for iCh, channel in enumerate(channels[slot]):
            hvModule.setParameter(handle,slots[slot],b"Pw",channel,1) #switch ON HV channel
            hvModule.setChName(handle,slots[slot],channel,chName[slot][iCh]) #Set name as defined in config file

    ######################
    #                    #
    # Setup oscilloscope #
    #                    #
    ######################
    useScope = False #If True -> use oscilloscope, set it up here
    if useScope:
        channels = [1,2,3,4] #List of active channels
        scope = TeledyneLeCroyPy.LeCroyWaveRunner('VICP::90.147.203.158') #Connect to scoper via TCP/IP
        scope.set_tdiv('20NS') #Set time base division of the scope
        
        for i in channels:
            scope.set_vdiv(i,0.5) #Set amplitude of all channels (1V peak to peak)
        #scope.set_vdiv(1,0.5) #Amplitude in volts channel 1 (1V peak to peak)
        #scope.set_vdiv(2,0.5) #Amplitude in volts channel 2 (1V peak to peak)
        #scope.set_vdiv(3,0.5) #Amplitude in volts channel 3 (1V peak to peak)
        #scope.set_vdiv(4,0.5) #Amplitude in volts channel 4 (1V peak to peak)
        scope.set_trig_mode('Ext') #External trigger
        scope.set_trig_level('Ext',-0.5) #-0.5 V -> for NIM signal (-0.9 V)
        scope.set_trig_slope('Negative') #Falling edge for NIM signal

    #Define general filename for DIP + CAEN + DAQ .root and WAVE.txt (oscilloscope data) output file
    dipOut = "scan_"+str(newRun)+"_DIP_"
    caenOut = "scan_"+str(newRun)+"_CAEN_"
    daqOut = "scan_"+str(newRun)+"_DAQ_"
    waveOut = "scan_"+str(newRun)+"_WAVE_"


    ################################
    #                              #
    # Begin for cycle on HV points #
    #                              #
    ################################
    for i in range(int(len(constants.measTime))):
        
        print("Number of triggers: ",trigNum[i])

        #Create TTree to save DAQ data
        treeDAQ = ROOT.TTree("treeDAQ","Data from TDCs")
        treeDAQ.Branch('eventNumber', eventNumber, 'eventNumber/I')
        treeDAQ.Branch('size', size, 'size/I')
        treeDAQ.Branch("channels",aChannels,'channels[size]/I') 
        treeDAQ.Branch("times",aTimes,'times[size]/F')

        #Start veto while TDC configuration is ongoing
        print("starting pulser")
        VMEbridge.configPulser(handle,0,1,40000000,0,0,0,0)
        VMEbridge.setOutputConf(handle,0,0,0,6)
        VMEbridge.startPulser(handle,0)
        
        #Configure TDCs
        print("\n configuring TDCs \n")

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
        VMEbridge.confScaler(handle,0,0,1,0,0)
        VMEbridge.enableScalerGate(handle)

        print("\n Scaler counts:",VMEbridge.readRegister(handle,0x1D))

        VMEbridge.enableIRQ(handle,111)
        
        if debug:
            print(i)
    
        print("Scanning point:",i+1)

        scanFol = "/home/pcald32/runs/efficiencyScans/scan_"+str(newRun)+"/HV_"+str(i+1)
        if not os.path.exists(scanFol):
            os.makedirs(scanFol)

        #Go in the folder and create root files
        dipOut = dipOut+"HV"+str(i+1)+".root" 
        caenOut = caenOut+"HV"+str(i+1)+".root"
        daqOut = daqOut+"HV"+str(i+1)+".root" 
        waveOut = waveOut+"HV"+str(i+1)+".txt"

        os.chdir(scanFol)

        fOutDIP = ROOT.TFile(dipOut,"RECREATE")
        fOutCAEN = ROOT.TFile(caenOut,"RECREATE")
        fOutDAQ = ROOT.TFile(daqOut,"RECREATE")
        if useScope: #Create output .txt file for oscilloscope data
            fOutWAVE = open(waveOut, mode="wt")

        os.chdir("/home/pcald32/labStrada/DAQ/efficiencyScan")

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

        #################################################################################
        #                                                                               #
        # Define process for HV correction and scope writing to be exectued in parallel #
        #                                                                               #
        #################################################################################
        print("Memory address of hTemp in main: ", id(hTemp))
        print("Memory address of hPress in main: ", id(hPress))
        print("Memory address of hHumi in main: ", id(hHumi))
        print("Memory address of hFlow in main: ", id(hFlow))
        print("Memory address of hHVeff in main: ", id(hHVeff))
        print("Memory address of hHVapp in main: ", id(hHVapp))
        print("Memory address of hHVmon in main: ", id(hHVmon))
        print("Memory address of hImon in main: ", id(hImon))

        hvCorrProc = Process(target=applyPTCorr, args=[mydb,mycursor,hTemp,hPress,hHumi,hFlow,
                                                    hvModule,handle,slots,channels,hHVeff,
                                                    hHVapp,hHVmon,hImon,effHV,i])
        if useScope:
            writeScopeProc = Process(target=writeScope,args=[scope,waveOut,channels])

        #First ramp up/down of voltage at the start of the scan
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

        #Test for filling histos at least once during inital ramp up
        #hTemp.Fill(temperature) #Fill temperature histo
        #hPress.Fill(pressure) #Fill pressure histo

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

        printedMessage = False #boolean to check if "channels are ramping" message has already been printed
        #Check if the channels are ramping
        while getStatus(hvModule,handle,totChannels,slots,channels) == True:
            if printedMessage == False: #Print message only once
                printedMessage = True
                print("Channels are ramping")
            
            time.sleep(2) #sleep for two seconds to relax a bit, not needed but ok, it can be used

        print("Ramping completed")

        hvModule.disconnect(handle) #disconnect from mainframe during waiting time

        #Sleep for duration of waiting time (connection with HV module is already closed here)
        print("Waiting for waiting time")
        print(constants.waitTime[i],"s")
        time.sleep(int(constants.waitTime[i]))
        print("Waiting time over")

        hvModule.connect()
        time.sleep(2)

        #Remove veto and start timer for PT correction
        VMEbridge.stopPulser(handle,0) #remove veto
        start = time.perf_counter() #start timer
    
        #Since we use the bridge to count the number of triggers and it has only 10 bits (up to 1023)
        #and once it reaches the limit it is automatically reset, every 1000 triggers this variable is increased
        #by 1000 to keep track of how many 1000 triggers we got
        contaMille = 0
        
        #PT correction every 30 seconds, executed in parallel to the rest of the code
        #started here because in the while loop it was giving an error
        hvCorrProc.start()
        mydb.connect()

        if hex(VMEbridge.checkIRQ(handle)) == hex(0x0):
            waitingIRQ = True
            print("Waiting for IRQ")
    
        while waitingIRQ:

            #hvCorrProc.start()
            """
            if time.perf_counter() - start > 30: #more than 30 seconds since last measurement
                VMEbridge.startPulser(handle,0) #start pulser (veto) during PT correction
                start = time.perf_counter() #Update last time of correction
                mydb.cmd_refresh(1) #refresh db to get last entry
            
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
                        print("i",i)
                        print("slot",slot)
                        print("iCh",iCh)
                        print("channel",channel)
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

                VMEbridge.stopPulser(handle,0)
            """

            #1000 triggers in the VME scaler -> increase contaMille
            if VMEbridge.readRegister(handle,0x1D) == int(hex(1000),16):
                #print("\n Increasing contaMille:\n")
                #print("Counts before: ", VMEbridge.readRegister(handle,0x1D))
                contaMille = contaMille+1000
                #print("Resetting scaler counter")
                VMEbridge.resetScalerCount(handle)
                #print("Counts after: ", VMEbridge.readRegister(handle,0x1D))

            if (contaMille + VMEbridge.readRegister(handle,0x1D))>=int(hex(trigNum[i]),16): #For noise scans with > 4096 triggers
                print("Desidered trigger number reached, moving to the next HV point, case 1")
                print("contaMille, case 1: ",contaMille)
                print("Numero di trigger impostati, case 1: ",int(hex(trigNum[i]),16))
                print("Numero di trigger calcolati, case 1: ",contaMille + int(VMEbridge.readRegister(handle,0x1D)))
                
                os.chdir(scanFol)

                fOutDAQ.cd()
                treeDAQ.Write()

                fOutCAEN.cd()
                ch = 0
                for slot in range(len(slots)):
                    for iCh, channel in enumerate(channels[slot]):
                        hHVapp[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_app_"+str(i+1))
                        hHVeff[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_eff_"+str(i+1))
                        hHVmon[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_mon_"+str(i+1))
                        hImon[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_I_mon_"+str(i+1))
                        ch=ch+1

                hvCorrProc.terminate() #Stop PT correction process when changing from one HV point to the other

                fOutDIP.cd()
                hTemp.Write("Temperature_HV_"+str(i+1))
                hPress.Write("Pressure_HV_"+str(i+1))
                hHumi.Write("Humidity_HV_"+str(i+1))
                hFlow.Write("Flow_HV_"+str(i+1))

                os.chdir("/home/pcald32/labStrada/DAQ/efficiencyScan")
                
                break
        
            else: #We have an IRQ from one or more TDCs
                VMEbridge.stopPulser(handle,0)
                IRQlevel = hex(VMEbridge.checkIRQ(handle))
                event = []

                #Event number taken from the bridge register to be saved in the tree
                eventNumber[0] = contaMille + VMEbridge.readRegister(handle,0x1D) 
                
                #Write oscilloscope data (if the variable is true)
                if useScope:
                    waveOut.write(str(eventNumber[0])+"\n") #Write trigger number to the output .txt file
                    writeScopeProc.start() #write function started in parallel

                #Send veto signal while IRQ is still active (TDC) 
                #And data is being written by the oscilloscope (this could be slow so we prefer to wait)
                while IRQlevel != hex(0x0): 
                #while IRQlevel != hex(0x0) and writeScopeProc.is_alive():
                    #VMEbridge.disableIRQ(handle,111)

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
                    print("\n", "Header 0:",header[0],"\n")
                    
                    for ch in range(header[0]):
                        print("ch", ch)
                        event.append(TDCs[whichTDC].readOutputBuffer(VMEbridge,handle))
                        #print("\ntime:",TDCs[whichTDC].converter(TDCs[whichTDC].readOutputBuffer(VMEbridge,handle)))

                    print("\n",event,"\n")

                    IRQlevel = hex(VMEbridge.checkIRQ(handle))
                    print("IRQ level a fine loop ",IRQlevel)
                    
                    if IRQlevel == hex(0x0):
                        print(type(event), event)
                        lChannels,lTimes = map(list,zip(*event))
                        print(lChannels, lTimes)
                        
                        size[0] = len(lChannels) #number of channels with a hit per event
                        
                        #Fill tree
                        for j in range(len(lChannels)):
                            aChannels.append(lChannels[j])
                            aTimes.append(lTimes[j])
                        
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
                        print("contamille",contaMille)

                        if (contaMille + VMEbridge.readRegister(handle,0x1D))>=int(hex(trigNum[i]),16): #For noise scans with > 4096 triggers
                            print("Desidered trigger number reached, moving to the next HV point, case 2")
                            print("contaMille, case 2: ",contaMille)
                            print("Numero di trigger impostati, case 2: ",int(hex(trigNum[i]),16))
                            print("Numero di trigger calcolati, case 2: ",contaMille + int(VMEbridge.readRegister(handle,0x1D)))
                            os.chdir(scanFol)

                            fOutDAQ.cd()
                            treeDAQ.Write()

                            fOutCAEN.cd()
                            ch = 0
                            for slot in range(len(slots)):
                                for iCh, channel in enumerate(channels[slot]):
                                    hHVapp[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_app_"+str(i+1))
                                    hHVeff[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_eff_"+str(i+1))
                                    hHVmon[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_HV_mon_"+str(i+1))
                                    hImon[ch].Write(str(chName[slot][iCh].decode('utf-8'))+"_I_mon_"+str(i+1))
                                    ch=ch+1

                            hvCorrProc.terminate() #Stop PT correction process when changing from one HV point to the other

                            fOutDIP.cd()
                            hTemp.Write("Temperature_HV_"+str(i+1))
                            hPress.Write("Pressure_HV_"+str(i+1))
                            hHumi.Write("Humidity_HV_"+str(i+1))
                            hFlow.Write("Flow_HV_"+str(i+1))

                            os.chdir("/home/pcald32/labStrada/DAQ/efficiencyScan")
                            break

                        VMEbridge.enableIRQ(handle,111)
                        #event.clear()
                        time.sleep(1)

                    #exit from wait for IRQ loop
                    #break

        #Reset names and increase HV point counter
        dipOut = "scan_"+str(newRun)+"_DIP_"
        caenOut = "scan_"+str(newRun)+"_CAEN_"
        daqOut = "scan_"+str(newRun)+"_DAQ_"

        fOutDAQ.Close()
        fOutCAEN.Close()
        fOutDIP.Close()

    #Delete tree for next HV point
    del treeDAQ

    print("\n\n --- Efficiency scan is over --- \n\n")

    #Set desired voltage on the RPC at the end of the scan
    if arguments[4] == "": #HV to set after the scan was NOT provided by the -> Set 0 V and switch off the channels
        switchOff(handle,hvModule,slots,channels,0)
    
    else: #HV to set after the scan was provided by the user -> apply the set voltagete
        switchOff(handle,hvModule,slots,channels,float(arguments[4]))

    hvModule.disconnect(handle)
    print("Disconnected from HV module")

    #Insert date and time of the end of the scan in the db
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    endTimeRun = [now,newRun]
    sendEndTime = "UPDATE efficiencyScan SET endDate = (%s) WHERE runNumber = (%s)"
    mycursor.execute(sendEndTime, endTimeRun)
    mydb.commit()

if __name__ == "__main__":
    main()
