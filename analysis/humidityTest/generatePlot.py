from audioop import avg
from doctest import debug
import math
from operator import le
from pickle import TRUE
from poplib import CR
from sqlite3 import Timestamp
from xmlrpc.client import DateTime
import numpy as np #numpy
import ctypes #for C++ function binding (CAEN HV library for example)
import pathlib #for library paths (to use C++ libraries in python)
import mysql.connector #to connect to db to send the data
import os  #To create new folders and so on
import ROOT #Root CERN functions
import time #For functions such as sleep
from datetime import datetime #To get date, time and perform operations on them
#import datetime #To get date, time and perform operations on them
import csv
from collections import defaultdict
import decimal
import pandas as pd
from array import array

def graphCosmetics(gIn,gTitle,gName,xAxisTitle,yAxisTitle,markerStyle,markerSize,markerColor,isTime):
    gIn.SetTitle(gTitle)
    gIn.SetName(gName)
    gIn.GetXaxis().SetTitle(xAxisTitle)
    gIn.GetYaxis().SetTitle(yAxisTitle)
    gIn.SetMarkerStyle(markerStyle)
    gIn.SetMarkerSize(markerSize)
    gIn.SetMarkerColor(markerColor)
    gIn.GetXaxis().SetLabelFont(62)
    gIn.GetYaxis().SetLabelFont(62)
    gIn.GetXaxis().SetTitleFont(62)
    gIn.GetYaxis().SetTitleFont(62)
    gIn.GetXaxis().SetTitleSize(0.05)
    gIn.GetYaxis().SetTitleSize(0.05)
    gIn.GetXaxis().SetLabelSize(0.05)
    gIn.GetYaxis().SetLabelSize(0.05)
    gIn.GetXaxis().CenterTitle(True)
    gIn.GetYaxis().CenterTitle(True)
    if isTime:
        gIn.GetXaxis().SetTimeDisplay(1)
        gIn.GetXaxis().SetTimeOffset(0)
        gIn.GetXaxis().SetNdivisions(-510)
        gIn.GetXaxis().SetTimeFormat("%m-%d %H:%M")

    return gIn
    

def getCurrTot(mycursor, timeIn, timeFin):
    getCurr = ("SELECT date,iMon FROM CAEN WHERE chName = '--GIF_temp-' And date BETWEEN '" + timeIn + "' AND '" + timeFin + "'")
    mycursor.execute(getCurr)
    curr = mycursor.fetchall()
    return curr

def getTLabAll(mycursor, timeIn, timeFin):
    getEnv = ("SELECT date,temperature,pressure,humidity FROM envPar WHERE date BETWEEN '" + timeIn + "' AND '" + timeFin + "'")
    mycursor.execute(getEnv)
    lastEnvT = mycursor.fetchall()
    return lastEnvT

def getTChamberAll(mycursor, timeIn, timeFin):
    getEnv = ("SELECT date,humidity,temperature,envHumi FROM humidityTest WHERE date BETWEEN '" + timeIn + "' AND '" + timeFin + "'")
    mycursor.execute(getEnv)
    lastEnvT = mycursor.fetchall()
    return lastEnvT

def getTChamber(mycursor, timeIn, timeFin):
    getEnv = ("SELECT AVG(temperature), MIN(temperature), MAX(temperature) FROM humidityTest WHERE date BETWEEN '" + timeIn + "' AND '" + timeFin + "'") 
    mycursor.execute(getEnv)
    lastEnvT = mycursor.fetchall()
    return lastEnvT

def getTLab(mycursor, timeIn, timeFin):
    #getLastEnv = ("SELECT temperature FROM envPar WHERE date BETWEEN '" + timeIn + "' AND '" + timeFin + "'")
    #mycursor.execute(getLastEnv)
    getEnv = ("SELECT AVG(temperature), MIN(temperature), MAX(temperature) FROM envPar WHERE date BETWEEN '" + timeIn + "' AND '" + timeFin + "'") 
    mycursor.execute(getEnv)
    lastEnvT = mycursor.fetchall()
    return lastEnvT

def main():

    debug = False

    #connects to the dd
    mydb = mysql.connector.connect( #db object on localhost
        host="localhost",
        user="root",
        password="pcald32",
        database="labStrada"
    )

    mycursor = mydb.cursor()

    #List to copy the content of the configFile
    scans = []

    #Open txt file with all runs
    with open("/home/pcald32/labStrada/analysis/humidityTest/iHvTestOrNot.txt") as configFile:
        scanPoints = configFile.readlines()
        if debug:
            print(scanPoints)
        
        scanPoints.pop(0)

        for point in scanPoints:
            if debug:
                print(point)
            
            asList = point.split("\t")

            if debug:
                print(asList)
            
            scans.append(asList)
    
    if debug:
        print(scans)

    #times = x axis for graph (date of the runs), runs = y axis for graph (run numbers)
    times, runs = array( 'd' ), array( 'd' )

    for scan in scans:
        times.append(ROOT.TDatime(scan[2]).Convert())
        runs.append(float(scan[1]))
    
    if debug:
        print(times)
        print(runs)

    gRunTime = ROOT.TGraph(len(times), times, runs)
    cRuns = ROOT.TCanvas("cRuns","cRuns",1200,1200)
    cRuns.cd()

    gRunTime.SetTitle('Runs (t)')
    gRunTime.SetName('Runs (t)')
    gRunTime.GetXaxis().SetTitle('Time [UTC]')
    gRunTime.GetYaxis().SetTitle('Run #')
    gRunTime.GetXaxis().SetLabelFont(62)
    gRunTime.GetYaxis().SetLabelFont(62)
    gRunTime.SetMarkerStyle(8)
    gRunTime.SetMarkerColor(1)
    gRunTime.SetMarkerSize(0)
    gRunTime.GetXaxis().SetTimeDisplay(1)
    gRunTime.GetXaxis().SetTimeOffset(0)
    gRunTime.GetXaxis().SetNdivisions(509)
    gRunTime.GetXaxis().SetTimeFormat("%m-%d %H:%M")
    gRunTime.SetMinimum(0)
    
    gRunTime.Draw("AP")
    #cRuns.Update()

    maxRun = gRunTime.GetHistogram().GetMaximum()

    flowStop = "2023-11-24 15:40:58"
    lStopFlow = ROOT.TLine(ROOT.TDatime(flowStop).Convert(),0,ROOT.TDatime(flowStop).Convert(),maxRun)
    lStopFlow.SetLineWidth(2)
    lStopFlow.SetLineColor(ROOT.kBlack)

    noHumiStart1 = "2023-11-26 18:44:18"
    noHumiEnd1 = "2023-11-27 10:45:45"

    lNoHumiStart1 = ROOT.TLine(ROOT.TDatime(noHumiStart1).Convert(),0,ROOT.TDatime(noHumiStart1).Convert(),maxRun)
    lNoHumiEnd1 = ROOT.TLine(ROOT.TDatime(noHumiEnd1).Convert(),0,ROOT.TDatime(noHumiEnd1).Convert(),maxRun)
    lNoHumiStart1.SetLineWidth(2)
    lNoHumiStart1.SetLineColor(ROOT.kRed)
    lNoHumiEnd1.SetLineWidth(2)
    lNoHumiEnd1.SetLineColor(ROOT.kRed)

    tempExtStart = "2023-11-29 20:10:28"
    tempExtStop = "2023-12-02 08:23:01"

    ltempExtStart = ROOT.TLine(ROOT.TDatime(tempExtStart).Convert(),0,ROOT.TDatime(tempExtStart).Convert(),maxRun)
    ltempExtStop = ROOT.TLine(ROOT.TDatime(tempExtStop).Convert(),0,ROOT.TDatime(tempExtStop).Convert(),maxRun)
    ltempExtStart.SetLineWidth(2)
    ltempExtStart.SetLineColor(ROOT.kSpring)
    ltempExtStop.SetLineWidth(2)
    ltempExtStop.SetLineColor(ROOT.kSpring)

    noHumiStart2 = "2023-12-02 14:20:32"
    noHumiEnd2 = "2023-12-04 17:49:47"

    lNoHumiStart2 = ROOT.TLine(ROOT.TDatime(noHumiStart2).Convert(),0,ROOT.TDatime(noHumiStart2).Convert(),maxRun)
    lNoHumiEnd2 = ROOT.TLine(ROOT.TDatime(noHumiEnd2).Convert(),0,ROOT.TDatime(noHumiEnd2).Convert(),maxRun)
    lNoHumiStart2.SetLineWidth(2)
    lNoHumiStart2.SetLineColor(ROOT.kMagenta)
    lNoHumiEnd2.SetLineWidth(2)
    lNoHumiEnd2.SetLineColor(ROOT.kMagenta)

    lStopFlow.Draw("SAME")
    lNoHumiStart1.Draw("SAME")
    lNoHumiEnd1.Draw("SAME")
    ltempExtStart.Draw("SAME")
    ltempExtStop.Draw("SAME")
    lNoHumiStart2.Draw("SAME")
    lNoHumiEnd2.Draw("SAME")
   
    #x and y coordinates obtained from all the points in the TGraph
    xCoord = ctypes.c_double(0)
    yCoord = ctypes.c_double(0)
    mList = list()
    for i in range(gRunTime.GetN()):
        gRunTime.GetPoint(i,xCoord,yCoord)
        x = xCoord.value
        y = yCoord.value
        #print("x ",x)
        mList.append(ROOT.TMarker(x,y,8))
        
        if (x <= ROOT.TDatime(flowStop).Convert()) or (x <= ROOT.TDatime(noHumiEnd2).Convert() and x >= ROOT.TDatime(noHumiStart2).Convert()): #run is not analyzed
            mList[i].SetMarkerColor(ROOT.kRed)
        
        else: #run is analyzed
            mList[i].SetMarkerColor(ROOT.kSpring)
        
        mList[i].Draw("SAME")

    cRuns.Update()

    #Get highest/lowest temperature per day
    startTime = "2023-11-23 18:00:56" #start time as a string
    startTimeStamp = ROOT.TDatime(startTime).Convert() #Convert to timestamp to make calculations
    print("startTimeStamp:",type(startTimeStamp))
    
    strStartTime = (datetime.fromtimestamp(startTimeStamp)).strftime("%Y-%m-%d %H:%M:%S") #Convert back to string
    print("strStartTime:",type(strStartTime))

    avgTemp = array('d')
    minTemp = array('d')
    maxTemp = array('d')
    exLow = array('d')
    exHigh = array('d')
    day = array('d')

    for i in range (24):
        endTimeStamp = startTimeStamp + 86400 #Get end of day in timestamp

        #Convert to string for mysql query
        strStartDay = (datetime.fromtimestamp(startTimeStamp)).strftime("%Y-%m-%d %H:%M:%S")
        strEndDay = (datetime.fromtimestamp(endTimeStamp)).strftime("%Y-%m-%d %H:%M:%S")
        
        #Get environmental parameters
        #Sometimes it happend that the sensor close to the chamber stopped sending data, hence we take 
        #them from the other PT sensor
        if startTimeStamp >= ROOT.TDatime(noHumiStart1).Convert() and endTimeStamp <= ROOT.TDatime(noHumiEnd1).Convert():
            print("Getting T Lab")
            env = getTLab(mycursor,strStartDay,strEndDay)
        else:
            print("Getting T chamber")
            env = getTChamber(mycursor,strStartDay,strEndDay)
        
        if debug:
            print(env)

        if env[0][0] != None: #if one of the parameter is "None" -> no data in that period, so skip it
            avgTemp.append(env[0][0])
            minTemp.append(env[0][0]-env[0][1])
            maxTemp.append(env[0][2]-env[0][0])
            day.append(startTimeStamp)
            exLow.append(0)
            exHigh.append(0)

        if debug:
            print("Day ", i+1, " start: ", startTimeStamp, " end ", endTimeStamp)

        startTimeStamp = endTimeStamp #Update for the start of the next day

    if debug:
        print("len avgTemp ", len(avgTemp))
        print("avgTemp ",avgTemp)
        print("len minTemp ", len(minTemp))
        print("minTemp ",minTemp)
        print("len maxTemp ", len(maxTemp))
        print("maxTemp ",maxTemp)
        print("len day ",len(day))
        print("day ",day)

    grTempMaxMin = ROOT.TGraphAsymmErrors(len(avgTemp),day,avgTemp,exLow,exHigh,minTemp,maxTemp)
    graphCosmetics(grTempMaxMin,"","Max-min temperature (t)","Time [UTC]","Max-min Temperature [#circC]",8,2,ROOT.kBlack,True)
    grTempMaxMin.GetXaxis().SetNdivisions(509)

    cTempMaxMin = ROOT.TCanvas("cTempMaxMin","cTempMaxMin",1200,1200)
    cTempMaxMin.cd()
    grTempMaxMin.Draw("AP")
    cTempMaxMin.Update()
    
    #Plot gloabl trends of environmental parameters
    getLastDateLab = ("SELECT date FROM envPar ORDER BY date DESC LIMIT 1") #Lab
    mycursor.execute(getLastDateLab)

    endTimeLab = mycursor.fetchall()

    getLastDateChamber = ("SELECT date FROM humidityTest ORDER BY date DESC LIMIT 1") #Chamber
    mycursor.execute(getLastDateChamber)

    endTimeChamber = mycursor.fetchall()

    #print(type(endTimeChamber[0][0]))
    
    endTime = str(datetime.now()) #end date for these plots is the current date and time
    
    envTotChamber = getTChamberAll(mycursor,startTime,str(endTimeChamber[0][0]))
    print(len(envTotChamber))

    envTotLab = getTLabAll(mycursor,startTime,str(endTimeLab[0][0]))
    print(len(envTotLab))

    #To save data obtained close to the RPC
    totTempChamber, totGasHumiChamber, totEnvHumiChamber, totDateChamberGasHumi, totDateChamberEnvHumi, totDateChamberTemp  = array('d'), array('d'), array('d'), array('d'), array('d'), array('d')
    #To save data obtained from the general lab sensor
    totTempLab, totPressLab, totEnvHumiLab, totDateLabTemp, totDateLabPress, totDateEnvHumiLab = array('d'), array('d'), array('d'), array('d'), array('d'), array('d')

    for i in range(len(envTotChamber)):
        if envTotChamber[i][1] != None and envTotChamber[i][1] != 0:
            totDateChamberGasHumi.append(datetime.timestamp(envTotChamber[i][0]))
            totGasHumiChamber.append(envTotChamber[i][1])
        if envTotChamber[i][2] != None:
            totDateChamberTemp.append(datetime.timestamp(envTotChamber[i][0]))
            totTempChamber.append(envTotChamber[i][2])
        if envTotChamber[i][3] != None:
            totDateChamberEnvHumi.append(datetime.timestamp(envTotChamber[i][0]))
            totEnvHumiChamber.append(envTotChamber[i][3])

    for i in range(len(envTotLab)):
        if envTotLab[i][1] != None:
            totDateLabTemp.append(datetime.timestamp(envTotLab[i][0]))
            totTempLab.append(envTotLab[i][1])
        if envTotLab[i][2] != None:
            totDateLabPress.append(datetime.timestamp(envTotLab[i][0]))
            totPressLab.append(envTotLab[i][2])
        if envTotLab[i][3] != None:
            totDateEnvHumiLab.append(datetime.timestamp(envTotLab[i][0]))
            totEnvHumiLab.append(envTotLab[i][3])

    grTempTotChamber = ROOT.TGraph(len(totDateChamberTemp),totDateChamberTemp,totTempChamber)
    graphCosmetics(grTempTotChamber,"","Temperature (t)","Time [UTC]","Temperature [#circC]",8,1,ROOT.kAzure,True)
    grTempTotChamber.GetXaxis().SetLimits(ROOT.TDatime(startTime).Convert(),ROOT.TDatime(str(endTimeChamber[0][0])).Convert()); 

    grGasHumiTot = ROOT.TGraph(len(totDateChamberGasHumi),totDateChamberGasHumi,totGasHumiChamber)
    graphCosmetics(grGasHumiTot,"","Gas humidity (t)","Time [UTC]","Gas Humidity [%]",8,1,ROOT.kRed,True)
    grGasHumiTot.GetXaxis().SetLimits(ROOT.TDatime(startTime).Convert(),ROOT.TDatime(str(endTimeChamber[0][0])).Convert()); 

    grEnvHumi = ROOT.TGraph(len(totDateChamberEnvHumi),totDateChamberEnvHumi,totEnvHumiChamber)
    graphCosmetics(grEnvHumi,"","Ambient humidity (t)","Time [UTC]","Ambient Humidity [%]",8,1,ROOT.kGreen,True)
    grEnvHumi.GetXaxis().SetLimits(ROOT.TDatime(startTime).Convert(),ROOT.TDatime(str(endTimeChamber[0][0])).Convert()); 

    #Draw chamber env parameters
    cEnvChamber = ROOT.TCanvas("cEnvChamber","cEnvChamber",1200,1200)
    cEnvChamber.cd()
    cEnvChamber.Divide(1,3)
    cEnvChamber.cd(1)
    ROOT.gPad.SetTopMargin(0.02)
    grTempTotChamber.Draw("AP")
    cEnvChamber.cd(2)
    ROOT.gPad.SetTopMargin(0.02)
    grGasHumiTot.Draw("AP")
    cEnvChamber.cd(3)
    ROOT.gPad.SetTopMargin(0.02)
    grEnvHumi.Draw("AP")
    cEnvChamber.Update()

    grTempTotLab = ROOT.TGraph(len(totDateLabTemp),totDateLabTemp,totTempLab)
    graphCosmetics(grTempTotLab,"","Ambient temperature (t)","Time [UTC]","Ambient temperature [#circC]",8,1,ROOT.kAzure,True)
    grTempTotLab.GetXaxis().SetLimits(ROOT.TDatime(startTime).Convert(),ROOT.TDatime(str(endTimeLab[0][0])).Convert()); 

    grPressTotLab = ROOT.TGraph(len(totDateLabPress),totDateLabPress,totPressLab)
    graphCosmetics(grPressTotLab,"","Ambient pressure (t)","Time [UTC]","Atmospheric pressure [mbar]",8,1,ROOT.kRed,True)
    grPressTotLab.GetXaxis().SetLimits(ROOT.TDatime(startTime).Convert(),ROOT.TDatime(str(endTimeLab[0][0])).Convert()); 

    grEnvHumiLab = ROOT.TGraph(len(totDateEnvHumiLab),totDateEnvHumiLab,totEnvHumiLab)
    graphCosmetics(grEnvHumiLab,"","Ambient humidity (t)","Time [UTC]","Ambient humidity [%]",8,1,ROOT.kGreen,True)
    grEnvHumiLab.GetXaxis().SetLimits(ROOT.TDatime(startTime).Convert(),ROOT.TDatime(str(endTimeLab[0][0])).Convert()); 

    #Draw lab env parameters
    cEnvLab = ROOT.TCanvas("cEnvLab","cEnvLab",1200,1200)
    cEnvLab.cd()
    cEnvLab.Divide(1,3)
    cEnvLab.cd(1)
    ROOT.gPad.SetTopMargin(0.02)
    grTempTotLab.Draw("AP")
    cEnvLab.cd(2)
    ROOT.gPad.SetTopMargin(0.02)
    grPressTotLab.Draw("AP")
    cEnvLab.cd(3)
    ROOT.gPad.SetTopMargin(0.02)
    grEnvHumiLab.Draw("AP")
    cEnvLab.Update()

    #Plot total current and calculate charge integrated in the studies
    dateTotCurr, dateIntcharge, totCurr, intCharge = array('d'), array('d'), array('d'), array('d')
    chamberArea = 2500.

    curr = getCurrTot(mycursor,startTime,endTime)

    #Get current and dates
    for i in range(len(curr)):
        if curr[i][1] != None:
            dateTotCurr.append(datetime.timestamp(curr[i][0]))
            totCurr.append(curr[i][1])
    
    #Calculate int charge
    partialCharge = 0.
    for i in range(1,len(totCurr)):
        dateIntcharge.append(dateTotCurr[i])
        partialCharge += ((totCurr[i]+totCurr[i-1])*(dateTotCurr[i]-dateTotCurr[i-1]))/2
        intCharge.append((partialCharge*1e-3)/chamberArea)

    if debug:
        print("len dateTotCurr ",len(dateTotCurr)," len TotCurr ", len(totCurr)," len dateIntcharge ", len(dateIntcharge), " len intcharge ", len(intCharge))
    
    grTotCurr = ROOT.TGraph(len(dateTotCurr),dateTotCurr,totCurr)
    graphCosmetics(grTotCurr,"","Current (t)","Time [UTC]","Current [#muA]",8,0.1,ROOT.kGreen,True)
    grTotCurr.GetXaxis().SetLimits(ROOT.TDatime(startTime).Convert(),ROOT.TDatime(endTime).Convert()); 
    grTotCurr.GetXaxis().SetNdivisions(510)

    gIntCharge = ROOT.TGraph(len(dateIntcharge),dateIntcharge,intCharge)
    graphCosmetics(gIntCharge,"","Int charge (t)","Time [UTC]","Integrated charge [mC/cm^{2}]",8,0.1,ROOT.kRed,True)
    gIntCharge.GetXaxis().SetLimits(ROOT.TDatime(startTime).Convert(),ROOT.TDatime(endTime).Convert()); 
    gIntCharge.GetXaxis().SetNdivisions(510)

    #Draw current and int charge
    cCurr = ROOT.TCanvas("cCurr","cCurr",1200,1200)
    cCurr.cd()
    cCurr.Divide(1,2)
    cCurr.cd(1)
    ROOT.gPad.SetTopMargin(0.02)
    grTotCurr.Draw("AP")
    cCurr.cd(2)
    ROOT.gPad.SetTopMargin(0.02)
    gIntCharge.Draw("AP")
    cCurr.Update()

    input("Press enter to quit the program")

if __name__ == "__main__":
    main()