import os
import subprocess as sb
import logging
import time
import constants
from dotenv import dotenv_values
import mysql.connector #to connect to db to send the data
import ROOT #Root CERN functions
import sys
import shutil
from datetime import datetime #To get date, time and perform operations on them
import select
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

def getSourceAndAbStatus(mycursor):
    getSourceStatus = ("SELECT timestamp, sourceON FROM sourceDIP ORDER BY timestamp DESC LIMIT 1")
    mycursor.execute(getSourceStatus)
    lastSource = mycursor.fetchall()

    getABSstatus = ("SELECT timestamp, absUP, absDOWN FROM attDIP ORDER BY timestamp DESC LIMIT 1")
    mycursor.execute(getABSstatus)
    lastABS = mycursor.fetchall() 

    return lastSource, lastABS

#PT correction
def ptCorr(temp, press, hvEff):
  hvApp = hvEff*(constants.T0/temp)*(press/constants.p0)
  return hvApp

#Get last temp, press and humi from db
def getPT(mycursor):
    #getLastEnv = ("SELECT date, temperature, pressure FROM envPar ORDER BY date DESC LIMIT 1")
    getLastEnv = ("SELECT timestamp, TIN, P FROM envDIP ORDER BY timestamp DESC LIMIT 1")
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

    #Get arguments from command line (i.e. mixture and comments on the scan)
    arguments = sys.argv  #Get command line arguments (#0 =  mixture, #1 = scan type, #3 = comments, #4 = HV to set at the end of the scan)
                          #sys. argv[0] , represents the script name
    
    while len(arguments) < 3: #Check if size of arguments is smaller than 3 (it means that some argument is missing by mistake)
        #add "" until size 5 is reached, some information on the run will be lost but it doesn't matter
        arguments.append("")

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

    #Get last run number from db
    getLastRun = ("SELECT runNumber FROM digitizerRuns ORDER BY startDate DESC LIMIT 1")
    mycursor.execute(getLastRun)

    #Calculate new run number
    lastRun = mycursor.fetchall()

    if len(lastRun) != 0: #Empty, no runs yet in the db
        newRun = lastRun[0][0] + 1 #new run = last run + 1
    else:
        newRun = 1

    #Create folder to save the data locally
    newPath = "/home/pcald32/runs/digitizer/scan_"+str(newRun) 
    if not os.path.exists(newPath):
        os.makedirs(newPath)

    #Directory in external drive
    base_dir = "/media/pcald32/Extreme SSD/digitizer/"

    #start logging
    """
    logging.basicConfig(
        filename="/home/pcald32/runs/digitizer/scan_"+str(newRun)+"/log.txt",                      # File to write to
        filemode="w",                           # Overwrite each run; use 'a' to append
        level=#logging.info,                      # Log level
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    """
 
    #Get source status and ABS
    lastSource, lastABS = getSourceAndAbStatus(mycursor)
    sourceON = lastSource[0][1]
    absUP = lastABS[0][1]
    absDown = lastABS[0][2]

    print("Last source status is: ",sourceON, " abs UP: ", absUP, " abs DOWN: ", absDown)

    #Get command line values
    mixture = arguments[1]
    comments = arguments[2]
    lastHv = int(arguments[3])

    #logging.info(f"Starting scan {newRun}")
    print("newRun=",newRun)   # The line you want to catch
    
    #return

    if sourceON == 1:
        print("")
        #logging.info("Source status is ON")
    else:
        print("")
        #logging.info("Source status is OFF")

    #logging.info(f"Upstream ABS is {absUP} and downstream ABS is {absDown}")

    if lastHv == -1:
        print(f"Gas mixture is: ", mixture, " comment is: ", comments, " and last HV is: ",5000, " V")
        #logging.info(f"Gas mixture is:  {mixture}, the comment for the run is {comments} and last HV is: 5000 V")
    elif lastHv == 0:
        print(f"Gas mixture is: ", mixture, " comment is: ", comments, " and last HV is: ",0, " V")
        #logging.info(f"Gas mixture is:  {mixture}, the comment for the run is {comments} and last HV is: 0 V")
    elif lastHv == 1:
        print(f"Gas mixture is: ", mixture, " comment is: ", comments, " and last HV is the last one set")
        #logging.info(f"Gas mixture is:  {mixture}, the comment for the run is {comments} and last HV is the last voltage set")
    else:
        print(f"Gas mixture is: ", mixture, " comment is: ", comments, " and last HV is: ", lastHv)
        #logging.info(f"Gas mixture is:  {mixture}, the comment for the run is {comments} and last HV is {lastHV} V")

    #insert new run in db
    run = [newRun,mixture,sourceON,absUP,absDown,comments]
    sendNewRun = "INSERT INTO digitizerRuns (runNumber,mixture,sourceStatus,absUP,absDOWN,comments) VALUES (%s,%s,%s,%s,%s,%s)"
    mycursor.execute(sendNewRun, run)
    mydb.commit()

    #Get values from constants.py
    effHV = constants.effHV #Effective high voltage values
    slots = []
    slots = constants.slot #HV module slots
    channels = []
    channels = constants.channels #HV channels
    chName = []
    chName = constants.names #Channels name
    beamTrigNum = []
    rndmTrigNum = []

    #Calculate total number of channels to set proper HV values later on
    totChannels = sum([len(i) for i in channels])

    #Get the configuration of the run from the config file
    with open("/home/pcald32/labStrada/config/configGIFEffScan.txt") as configFile:
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

            constants.measTime.append(asList[length-4])
            constants.waitTime.append(asList[length-3])
            beamTrigNum.append(int(asList[length-2]))
            rndmTrigNum.append(int(asList[length-1].replace("\n", "")))

    print("Connecting to CAEN HV module")
    #logging.info("Connecting to CAEN HV module")
    hvModule = CAEN(b"128.141.151.206",b"admin",b"admin")

    #Connect to CAEN HV module
    handle = hvModule.connect()
    for slot in range(len(slots)):
        for iCh, channel in enumerate(channels[slot]):
            hvModule.setParameter(handle,slots[slot],b"Pw",channel,1)
            hvModule.setChName(handle,slots[slot],channel,chName[slot][iCh])

    #Loop over HV points
    for i in range(int(len(constants.measTime))):

        print("Scanning HV point: ", i+1)
        print("\n")
        print("Number of beam triggers: ",beamTrigNum[i])
        print("Number of random triggers: ",rndmTrigNum[i])
        print("\n")

        point = i+1
        #logging.info(f"Scanning HV{point} with {beamTrigNum[i]} beam triggers and {rndmTrigNum[i]} random triggers")

        #Create HV1, HV2,... folders in the run folder
        scanFol = "/home/pcald32/runs/digitizer/scan_"+str(newRun)+"/HV_"+str(i+1)+"/"
        if not os.path.exists(scanFol):
            os.makedirs(scanFol)

        #Go in the folder and create root files
        #Define general filename for DIP .root output file
        dipOut = scanFol+"scan_"+str(newRun)+"_DIP_HV"+str(i+1)+".root"
        caenOut = scanFol+"scan_"+str(newRun)+"_CAEN_HV"+str(i+1)+".root"

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
        #delta = (datetime.now() - lastDate).total_seconds() #Calculate difference between now and last measurement in the db
        delta = datetime.now().timestamp() - lastDate

        while delta > 1200: #1200 s = logger stopped for more than 20 minutes
            mydb.cmd_refresh(1)
            lastEnv = getPT(mycursor)
            lastDate = lastEnv[0][0]
            #delta = (datetime.now() - lastDate).total_seconds()
            delta = datetime.now().timestamp() - lastDate
            print("PT logging stopped more than 10 minutes ago!")
            print("Last PT saved is at:",str(lastDate))
            print("Pausing current scan until PT logging resumes") 
            #logging.erroror(f"PT logging stopped more than 10 minutes ago, last PT values are from {lastDate}, pausing scan until PT resumes") 
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
                #logging.info("Channels are ramping")
            
            time.sleep(2) #sleep for two seconds to relax a bit, not needed but ok, it can be used

        print("Ramping completed")

        #Disconnect from HV mainframe during waiting time
        hvModule.disconnect(handle) 
        
        print("Waiting for waiting time: ",constants.waitTime[i],"s")
        #logging.info(f"Waiting for waiting time: {constants.waitTime[i]} s")
        time.sleep(int(constants.waitTime[i]))
        print("Waiting time over")
        #logging.info(f"Waiting time over")

        #Reconnect to mainframe after waiting time
        hvModule.connect()
        time.sleep(2)

        ###########################
        #                         #
        # Launch wawedump program #
        #                         #
        ###########################

        #Reset digitizer usb port just to be extra safe
        #sb.run(["./usbReset.sh"])

        #Start wavedump 
        #cmd = ['/home/pcald32/wavedump-3.10.6/src/./wavedump', '/home/pcald32/wavedump-3.10.6/WaveDumpConfig.txt', str(beamTrigNum[i]),str(rndmTrigNum[i]),scanFol]
        cmd = ['/home/pcald32/wavedump-3.10.6/src/./wavedump', '/home/pcald32/wavedump-3.10.6/WaveDumpConfig_X742.txt', str(beamTrigNum[i]),str(rndmTrigNum[i]),scanFol]
        pWaveDump = sb.Popen(cmd)
        #pWaveDump = sb.Popen(cmd, stdout=sb.PIPE, stderr=sb.STDOUT, text=True, bufsize=1)        

        stampa = True
        
        #While wavedump is still taking data, do the HV scan and correction
        #If the wavedump has finished running, it will return a not None code and 
        #the while loop will be interrupted, the histograms will be saved and the code will move to the next HV point
        while pWaveDump.poll() is None:
            
            if stampa:
                print("Wavedump taking data...")
                #logging.info("Wavedump taking data...")
                stampa = False

            #Capture wavedump output to file
            """
            ready, _, _ = select.select([pWaveDump.stdout], [], [], 0.1)
            if ready:
                line = pWaveDump.stdout.readline()
                if line:
                    logger.info(f"[WaveDump] {line.strip()}")
            
            for line in pWaveDump.stdout:
                logger.info(f"[WaveDump] {line.strip()}")
            """
            globalIndex = 0
            
            lastEnv = getPT(mycursor)
            lastDate = lastEnv[0][0]
            #delta = (datetime.now() - lastDate).total_seconds() #Calculate difference between now and last measurement in the db
            delta = datetime.now().timestamp() - lastDate

            while delta > 1200:
                t_end = t_end + 3 #this is needed because the way to measure residual time is to compute t_end before the start of measuring time
                #but even if the PT logging is stopped, the time still passes. In this way we extend the end of run by 3 seconds, which is the waiting
                #time at the end of (while delta > 1200). This is precise to ~0.1 s, it can be improved by measuring how long the loop is but for the moment
                #it is good enough
                mydb.cmd_refresh(1)
                lastEnv = getPT(mycursor)
                lastDate = lastEnv[0][0]
                #delta = (datetime.now() - lastDate).total_seconds()
                delta = datetime.now().timestamp() - lastDate
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

    #All HV pints have been scanned
    print("\n\n --- Efficiency scan is over --- \n\n")

    #Set desired voltage on the RPC at the end of the scan
    #If argument was left blank - 5 kV stdby voltage
    if lastHv == 1: #HV to set after the scan was NOT provided by the -> Set 0 V and switch off the channels
        switchOff(handle,hvModule,slots,channels,5000)
    
    #else if 0 -> Set 0 V
    elif lastHv == 0:
        switchOff(handle,hvModule,slots,channels,0)

    #else if -1 -> leave last applied HV and do nothing
    elif lastHv == -1:
        hvModule.disconnect(handle)
    
    else: #HV to set after the scan was provided by the user -> apply the set voltagete
        switchOff(handle,hvModule,slots,channels,float(lastHv))

    hvModule.disconnect(handle)
    print("Disconnected from HV module")

    #Insert date and time of the end of the scan in the db
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    endTimeRun = [now,newRun]
    sendEndTime = "UPDATE digitizerRuns SET endDate = (%s) WHERE runNumber = (%s)"
    mycursor.execute(sendEndTime, endTimeRun)
    mydb.commit()

    print("Scan is over, disconnecting from HV mainframe")

    #Convert data to .root cern format and copy the original txt files to external drive
    print("\n\n --- Converting and analyzizng the data --- \n\n")

    for i in range(int(len(constants.measTime))):
        print("Converthing HV",i+1)

        arg1 = "/home/pcald32/runs/digitizer/scan_"+str(newRun)+"/HV_"+str(i+1)+"/"
        arg2 = "wave_"
        arg3 = i+1
        arg4 = "false"

        # Construct the command to compile and run the macro
        command = f'root -l -b -q \'convert2root.C+("{arg1}", "{arg2}", {arg3},"{arg4}")\''

        # Run the command
        try:
            sb.run(command, shell=True, check=True)
            print("ROOT macro executed successfully.")
        except sb.CalledProcessError as e:
            print(f"Error running ROOT macro: {e}")

        #Convert and copy to external drive
        print("Now copying file to external drive")
        
        scan_dir = base_dir + "scan_" + str(newRun) + "/"

        hv_dir = scan_dir + "HV_" + str(i+1)

        # Step 1: Create "scan_x" folder if it doesn't exist
        os.makedirs(scan_dir, exist_ok=True)

        # Step 2: Create "HV_y" folder inside "scan_x"
        os.makedirs(hv_dir, exist_ok=True)

        #Step 3: Copy files in the external drive
        for i in range(8):
            #src_file = arg1+"wave_"+str(i)+".txt"
            src_file = f"{arg1}wave_{i}.txt"
            dst_file = os.path.join(hv_dir, f"wave{i}.txt")
            if os.path.exists(src_file):
                shutil.copy(src_file, dst_file)
            else:
                print(f"Warning: {src_file} not found and was not copied.")
        
        #Step 4: Delete all .txt files
        for i in range(16):
            file_to_delete = f"{arg1}wave_{i}.txt"
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
            else:
                print(f"{file_to_delete} does not exist, skipping deletion.")

    #Analyze the data
    print("\n\n --- Analysis ongoing --- \n\n")

    arg1 = newRun
    arg2 = int(len(constants.measTime))

    # Construct the command to compile and run the macro
    commandAnalysis = f'root -l -b -q \'analyzeDigitizer.C+({arg1}, {arg2})\''

    try:
        sb.run(commandAnalysis, shell=True, check=True)
        print("Analysis results are located in folder: /home/pcald32/runs/digitizer/scan_"+str(newRun))
    except sb.CalledProcessError as e:
        print(f"Error running ROOT macro: {e}")
    

if __name__ == "__main__":
    main()