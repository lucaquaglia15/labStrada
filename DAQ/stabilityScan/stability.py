from ast import arg
from typing import NewType
import numpy as np #numpy
import mysql.connector #to connect to db to send the data
import ROOT #Root CERN functions
import time #For functions such as sleep
from datetime import datetime #To get date, time and perform operations on them
from dateutil.relativedelta import relativedelta
import os #To create new folders and so on
import sys #To perform system operation
import array
import constants
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
    getLastEnv = ("SELECT date, temperature, pressure FROM envPar ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastEnv)

    lastEnv = mycursor.fetchall()
    return lastEnv

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

#main function for current scan
debug = False

def main():

    print("---Stability scan starting---")

    secrets = dotenv_values("/home/pcald32/labStrada/.env")

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
    
    getLastRun = ("SELECT runNumber FROM stabilityScan ORDER BY date DESC LIMIT 1")
    mycursor.execute(getLastRun)

    #No runs in the db yet, put run number: 1 
    #if mycursor.fetchone() == None:
    #    print("Congratulations, you have just started your first stability scan")
    #    newRun = 1

    #After the first run
    #else:
    lastRun = mycursor.fetchall()
    newRun = lastRun[0][0] + 1 #new run = last run + 1

    #insert new run in db
    run = [newRun,arguments[1],arguments[2],arguments[3]] #A list is needed due to how mysql query works
    sendNewRun = "INSERT INTO stabilityScan (runNumber,mixture,runType,comments) VALUES (%s,%s,%s,%s)"
    mycursor.execute(sendNewRun, run)
    mydb.commit()

    #Create folder to save the data locally
    newPath = "/home/pcald32/runs/stabilityScans/scan_"+str(newRun) 
    
    if not os.path.exists(newPath):
        os.makedirs(newPath)

    #Get values from constants.py
    effHV = constants.effHV #Effective high voltage values
    slots = []
    slots = constants.slot #HV module slots
    channels = []
    channels = constants.channels #HV channels
    chName = []
    chName = constants.names #Channels name

    #Get the configuration of the run from the config file
    with open("/home/pcald32/labStrada/config/configStabScan.txt") as configFile:
        scanPoints = configFile.readlines()
        scanPoints.pop(0)
        
        for point in scanPoints:
            asList = point.split("\t")
            length = len(asList)

            iCh = 0
            for slot in range(len(slots)):
                for channel in enumerate(channels[slot]):
                    effHV[slot].append(asList[iCh])
                    iCh = iCh+1

            constants.waitTime.append(asList[length-1].replace("\n", ""))

    #Calculate total number of channels to set proper HV values later on
    totChannels = sum([len(i) for i in channels])

    print("Connecting to CAEN HV module")
    hvModule = CAEN(b"90.147.203.174",b"admin",b"admin")

    #Connect to CAEN HV module, switch ON channels and set the name
    handle = hvModule.connect()
    for slot in range(len(slots)):
        for iCh, channel in enumerate(channels[slot]):
            hvModule.setParameter(handle,slots[slot],b"Pw",channel,1)
            hvModule.setChName(handle,slots[slot],channel,chName[slot][iCh])
            #Create txt output file, create the file and close them here, we will write in them later on
            with open(newPath+"/"+chName[slot][iCh].decode("utf-8")+".txt", "w") as f:
                f.write("Time\tHVapp\tHVmon\tHVeff\tiMon\n")  # Write a line before closing
    
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
            hvApp = ptCorr(temperature, pressure, float(effHV[slot][iCh]))
            hvModule.setParameter(handle,slots[slot],b"V0Set",channel,hvApp)

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

    print("Waiting for waiting time")
    print(constants.waitTime[0],"s")
    time.sleep(int(constants.waitTime[0]))
    print("Waiting time over, starting stability run")

    hvModule.connect()
    time.sleep(2)

    #Write first line to output file
    for slot in range(len(slots)):
                    for iCh, channel in enumerate(channels[slot]):
                        hvApp = ptCorr(temperature, pressure, float(effHV[slot][iCh]))                        
                        hvMon = hvModule.getParameter(handle,slots[slot],b"V0Set",channel)
                        iMon = hvModule.getParameter(handle,slots[slot],b"IMon",channel)                
                        with open(newPath+"/"+chName[slot][iCh].decode("utf-8")+".txt", "a") as f:
                            f.write(str(int(datetime.now().timestamp())) + "\t" + str(f'{hvApp:.2f}') + "\t" + str(hvMon) + "\t" + str(effHV[slot][iCh]) + "\t" + str(f'{iMon:.2f}') + "\n")  

    #Beginning of the run
    startOfRun = datetime.now()

    #Start timer for PT correction
    start = time.perf_counter() #start timer

    #alive counter variable (increased by 1 for every iteration of the stability scan)
    aliveCounter = 0
   
   #Start stability scan -> simply correct HV and write data to txt file
    try:

        while True:

            #PT correction every 30 seconds
            if time.perf_counter() - start > 30: #more than 30 seconds since last measurement
                if aliveCounter % 20 == 0:
                    #Increase alive counter by 1
                    aliveCounter = aliveCounter+1
                    print("Correcting HV and saving to output txt files, alive counter: ", aliveCounter)

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

                for slot in range(len(slots)):
                    for iCh, channel in enumerate(channels[slot]):
                        #print("slot",slot)
                        #print("iCh",iCh)
                        #print("channel",channel)
                        hvApp = ptCorr(temperature, pressure, float(effHV[slot][iCh]))                        
                        hvModule.setParameter(handle,slots[slot],b"V0Set",channel,hvApp)
                        hvMon = hvModule.getParameter(handle,slots[slot],b"V0Set",channel)
                        iMon = hvModule.getParameter(handle,slots[slot],b"IMon",channel)
                                            
                        #print("Slot",slots[slot],"channel",channel,"hveff",effHV[slot][iCh],"hvApp",hvApp)
                        globalIndex = globalIndex+1
                        with open(newPath+"/"+chName[slot][iCh].decode("utf-8")+".txt", "a") as f:
                            f.write(str(int(datetime.now().timestamp())) + "\t" + str(f'{hvApp:.2f}') + "\t" + str(hvMon) + "\t" + str(effHV[slot][iCh]) + "\t" + str(f'{iMon:.2f}') + "\n")  
            
    except KeyboardInterrupt as e:   

        print("\n\n --- Stopping stability scan --- \n\n")

        #Set desired voltage on the RPC at the end of the scan
        if arguments[4] == "": #HV to set after the scan was NOT provided by the -> Set 0 V and switch off the channels
            switchOff(handle,hvModule,slots,channels,0)
        
        else: #HV to set after the scan was provided by the user -> apply the set voltagete
            switchOff(handle,hvModule,slots,channels,float(arguments[4]))

        hvModule.disconnect(handle)
        print("Disconnected from HV module")

        #Insert date and time of the end of the scan in the db
        endOfRun = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        endTimeRun = [endOfRun,newRun]
        sendEndTime = "UPDATE stabilityScan SET endDate = (%s) WHERE runNumber = (%s)"
        mycursor.execute(sendEndTime, endTimeRun)
        mydb.commit()
        endOfRun = datetime.strptime(endOfRun, "%Y-%m-%d %H:%M:%S")
        runDuration = relativedelta(endOfRun, startOfRun)
        time_diff = endOfRun - (startOfRun + relativedelta(years=runDuration.years, months=runDuration.months, days=runDuration.days))
        print("Stability run ended, duration: ",f"{runDuration.years} years:{runDuration.months} months:{runDuration.days} days {time_diff.seconds//3600:02} hrs:{(time_diff.seconds//60)%60:02} min:{time_diff.seconds%60:02} sec")

if __name__ == "__main__":
    main()