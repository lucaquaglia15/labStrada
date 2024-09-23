from audioop import avg
import math
from operator import le
from pickle import TRUE
from sqlite3 import Timestamp
from xmlrpc.client import DateTime
import numpy as np #numpy
import ctypes #for C++ function binding (CAEN HV library for example)
import pathlib #for library paths (to use C++ libraries in python)
import mysql.connector #to connect to db to send the data
import os  #To create new folders and so on
import ROOT #Root CERN functions
import time #For functions such as sleep
#from datetime import datetime #To get date, time and perform operations on them
import datetime #To get date, time and perform operations on them
import csv
from pandas_ods_reader import read_ods
from collections import defaultdict
import decimal
import pandas as pd


import sys #To perform system operation
from math import sin
from math import sqrt
from array import array


def getiHv(mycursor, timeIn, timeFin):
    getLastEnv = ("SELECT hvSet, hvMon, iMon FROM CAEN WHERE chName = '--GIF_temp-'  AND date BETWEEN '" + timeIn + "' AND '" + timeFin + "'")
    mycursor.execute(getLastEnv)

    lastEnvIHV = mycursor.fetchall()
    return lastEnvIHV

def getTChamber(mycursor, timeIn, timeFin):
    getLastEnv = ("SELECT temperature FROM humidityTest WHERE date BETWEEN '" + timeIn + "' AND '" + timeFin + "'")
    mycursor.execute(getLastEnv)

    lastEnvT = mycursor.fetchall()
    return lastEnvT

def getTLab(mycursor, timeIn, timeFin):
    getLastEnv = ("SELECT temperature FROM envPar WHERE date BETWEEN '" + timeIn + "' AND '" + timeFin + "'")
    mycursor.execute(getLastEnv)

    lastEnvT = mycursor.fetchall()
    return lastEnvT

def getPressureLab(mycursor, timeIn, timeFin):
    getLastEnv = ("SELECT AVG(pressure) FROM envPar WHERE date BETWEEN '" + timeIn + "' AND '" + timeFin + "'")
    mycursor.execute(getLastEnv)

    lastEnvP = mycursor.fetchall()
    return lastEnvP
    
 
def main():

    #HVeffTot = []
    base_path = "/home/pcald32/logBookHumiTest.ods"
    df = read_ods(base_path, 1, headers=True)
    HVeff= df["HV eff [V]"].tolist()
    Triggers= df["Trigger_#"].tolist()
    bin= df["File bin"].tolist()
    runNum= df["Run #"].tolist()

    #array of temperature normalized
    tempNormalized = array('d')

    #if this is true, debug printouts are enabled
    debug = False

    #List for Tgraph style inside the loop on all scans
    graphStyle = [*range(68,86,1)]

    #Canvas for the rates 2D maps
    c5 = ROOT.TCanvas('c5', 'Rates', 1200, 1200)

    #List of TH2F taken from the autotrigger analysis

    histos2D = list()

    init_q = 0
    init_m = 0

    #Output .root file
    fileOutput = ROOT.TFile("iHvScan.root","RECREATE")
    
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

    with open("/home/pcald32/labStrada/analysis/humidityTest/iHvTestOrNot.txt") as configFile:
        scanPoints = configFile.readlines()
        #print(scanPoints)
        scanPoints.pop(0)

        for point in scanPoints:
            asList = point.split("\t")
            scans.append(asList)
    
    temperature = []
    averageT = []

    yIHvTime = array('d')
    xIHvTimeIn = array('d')

    yITemperature = array('d')
    xITemperature = array('d')
    xRTemperature = array('d')
    xRTemperatureNorm = array('d')

    pressureLab = array('d')

    #TMultiGraph to to save all the I(HV) curves
    mCurrHV = ROOT.TMultiGraph("mg","")
    mCurrHV.GetXaxis().SetTitle("HV_{eff} [V]")
    mCurrHV.GetYaxis().SetTitle("Current density [#muA/cm^{2}]")
    mCurrHV.GetXaxis().CenterTitle(True)
    mCurrHV.GetYaxis().CenterTitle(True)
    mCurrHV.GetXaxis().SetTitleFont(62)
    mCurrHV.GetYaxis().SetTitleFont(62)
    mCurrHV.GetXaxis().SetLabelFont(62)
    mCurrHV.GetYaxis().SetLabelFont(62)
    mCurrHV.GetYaxis().SetTitleOffset(1.55)

    lCurr = ROOT.TLegend(0.78,0.50,0.94,0.89,"","rNDC")
    lCurr.SetBorderSize(0)	
    lCurr.SetFillStyle(0)	
    lCurr.SetTextFont(62)
    lCurr.SetTextSize(0.05)

    grCurrHv = list()
    c1 = ROOT.TCanvas('c1', 'I(HV)', 1200, 1200)
    c1.SetGrid()

    l1 = list()
    c2 = ROOT.TCanvas('c2', 'I(t)', 1200, 1200)
    c2.SetGrid()

    c3 = ROOT.TCanvas('c3', 'T(t)', 1200, 1200)
    c3.SetGrid()
    c3.Divide(1,3)

    c4 = ROOT.TCanvas('c4', 'I(Temperature)', 1200, 1200)
    c4.SetGrid()

    c28 = ROOT.TCanvas('c28', 'P(t)', 1200, 1200)
    c28.SetGrid()
    c28.Divide(1,3)


    grCurrHvSet = list()
    c16 = ROOT.TCanvas('c16', 'I(HvSet)', 1200, 1200)
    c16.SetGrid()
    inRun = 0

    l2 = list()
    l3 = list()
    #averageTemperatureList = []
    #averageCurrentList = []

    dicDateTime = {}
    dicTemperature = {}
    dicCurrent = {}
    dicHvSet = {}

    hv = 6000
    if hv == 6500:
        hvNumber = 0
    elif hv == 6000:
        hvNumber = 1
    elif hv == 5500:
        hvNumber = 2
    elif hv == 5000:
        hvNumber = 3
    elif hv == 4500:
        hvNumber = 4
    elif hv == 4000:
        hvNumber = 5
    elif hv == 3500:
        hvNumber = 6
    elif hv == 3000:
        hvNumber = 7
    elif hv == 2500:
        hvNumber = 8
    elif hv == 2000:
        hvNumber = 9
    elif hv == 1500:
        hvNumber = 10
    elif hv == 1000:
        hvNumber = 11
    else:
        hvNumber = 12
   

    #Loop in all scans
    for iRun, scan in enumerate(scans):       

        #List to contain hv mon, set and current in each scan
        hvMon = []  
        hvSet = []
        iMon = []
        errorsIMon = array('d')
        errorsTemperature = array('d')
        temperature = 0 #Temporary variable to calculate average temp in run
        temperatureAll = 0 
        counterTemp = 0 #To count how many temperature values during the run
        counterTempAll = 0
        sumsIMon = 0 ##Temporary variable to calculate average current at fixed HV
        sumsHvSet = 0
        sameHvCounter = 1 #To count # of HV values at fixed HV
        averageIMon = [] #Avegare currents during the run
        averageHvSet = [] #Avegare currents during the run
        iMonPerRun = [] #temporary list of the iMon for the same run
        hvSetPerRun = []
        allTemperatureAnalyzed = []
        resistanceList = []
        errResistance = array('d')
        resistanceArray = array('d')
        print(iRun)

        if int(scan[4]) == 1:
            dicDateTime[iRun+1] = scan[2]
        else:
            continue
        
        #print(type(dicDateTime))
        #Get CAEN parameters
        timeInAll = scan[2]
        timeFinAll = scan[3]
        if int(scan[1]) in range(31, 35, 1):
            lastEnvTAll = getTLab(mycursor, timeInAll, timeFinAll)
        
        elif int(scan[1]) in range(57,59,1):
                lastEnvTAll = getTLab(mycursor, timeInAll, timeFinAll)

        elif int(scan[1]) in range(70,72,1):
                lastEnvTAll = getTLab(mycursor, timeInAll, timeFinAll)
        
        elif int(scan[1]) in range(95,117,1):
            lastEnvTAll = getTLab(mycursor, timeInAll, timeFinAll)

        elif int(scan[1]) in range(199,205,1):
            lastEnvTAll = getTLab(mycursor, timeInAll, timeFinAll)
        
        elif int(scan[1]) == 93 or int(scan[1]) == 94:
            lastEnvTAll = getTLab(mycursor, timeInAll, timeFinAll)
        
        else:
            lastEnvTAll = getTChamber(mycursor, timeInAll, timeFinAll)
        
        lastEnvPressure = getPressureLab(mycursor, timeInAll, timeFinAll)

        pressureLab.append(lastEnvPressure[0][0])

        #print("pressioneLab: ", pressureLab)

        for i in lastEnvTAll:
            temperatureAll += i[0]
            counterTempAll += 1
            #Append average temperature of the run
            avgTempAll = temperatureAll/counterTempAll
            dicTemperature[iRun+1] = avgTempAll


        if int(scan[0]) == 0: #Scan is not to be considered, move to the next one
            print("Skipping scan ",scan[1])
            continue
        
        else: #Scan is analyzed
            #Start and end time of each scan from the .txt config file
            timeIn = scan[2]
            timeFin = scan[3]
            print("Analyzing scan: ", scan[1])

            #Get CAEN parameters
            lastEnvIHV = getiHv(mycursor, timeIn, timeFin)
            
            #Get env parameters
            if int(scan[1]) in range(31, 35, 1):
                lastEnvT = getTLab(mycursor, timeIn, timeFin)

            elif int(scan[1]) in range(57,59,1):
                lastEnvT = getTLab(mycursor, timeIn, timeFin)

            elif int(scan[1]) in range(70,72,1):
                lastEnvT = getTLab(mycursor, timeIn, timeFin)

            elif int(scan[1]) in range(95,117,1):
                lastEnvT = getTLab(mycursor, timeIn, timeFin)

            elif int(scan[1]) in range(199,205,1):
                lastEnvT = getTLab(mycursor, timeIn, timeFin)

            elif int(scan[1]) == 93 or int(scan[1]) == 94:
                lastEnvT = getTLab(mycursor, timeIn, timeFin)
        
            else:
                lastEnvT = getTChamber(mycursor, timeIn, timeFin)
             
            #Errors on iMon and temperature
            #deltaiMon = 0.1 #microA
            deltaT = 0.1 #Celsius degree
            
            #Append to lists the CAEN parameters
            for i in lastEnvIHV:
                hvSet.append(i[0])
                hvMon.append(i[1])
                iMon.append(i[2])
                #errorsIMon.append(deltaiMon)

            #Debug printouts
            if debug == True:
                print("Scan ",scan[1])
                print("\n")
                print(hvSet)

            #Calculate average temperature in run
            for i in lastEnvT:
                temperature += i[0]
                counterTemp += 1
                allTemperatureAnalyzed.append(i[0])
                
            if debug:
                print("allT: ", allTemperatureAnalyzed)

            noHumiStart2 = "2023-12-02 14:20:32"
            noHumiEnd2 = "2023-12-04 17:49:47"

            #Append averge temperature of the run
            avgTemp = temperature/counterTemp
            averageT.append(temperature/counterTemp)
            tempNormalized.append(avgTemp -21)

            for i in range(len(allTemperatureAnalyzed)):   
                std_numpy_T = np.std(allTemperatureAnalyzed)
                errAvT = std_numpy_T/(math.sqrt(len(allTemperatureAnalyzed)))
            
            if debug:
                print("Dev std I: ", std_numpy_T)
                print("Mean error I: ", errAvT)

            #Error on average temperature


            #Calculate average current and hvset per HV value -> inside a run
            for i in range(1, len(hvSet)):
                iMonPerRun.append(iMon[i-1])
                hvSetPerRun.append(hvSet[i-1])
                #print(i, iMon[i])
                if (hvSet[i]-hvSet[i-1]) > -50 :
                    sumsIMon += iMon[i-1]
                    sumsHvSet += hvSet[i-1]
                    sameHvCounter += 1
                    if debug:
                        print(hvSet[i])
                        print("Sto incrementando sameHvCounter ed e': ", sameHvCounter)
                else :
                    sumsIMon += iMon[i-1]
                    sumsHvSet += hvSet[i-1]
                    if debug:
                        print("Sto per calcolare la corrente media e sameHvCounter e': ", sameHvCounter)
                    averageIMon.append(sumsIMon/sameHvCounter)
                    averageHvSet.append(sumsHvSet/sameHvCounter)
                    sumsIMon = 0
                    sumsHvSet = 0
                    sameHvCounter = 1
                    if debug:
                        print("Riporto sameHvCounter a 1: ", sameHvCounter)
            #print("iMonPerRun: ",iMonPerRun)       
            for i in range(len(iMonPerRun)):   
                std_numpy_I = np.std(iMonPerRun)
                errAvI = (std_numpy_I/(math.sqrt(len(iMonPerRun))))*(10**(-6))
                #errAvI = (std_numpy_I/(math.sqrt(len(iMonPerRun))))
            for i in range(len(hvSet)):
                std_numpy_hvSet = np.std(hvSet)
                errAvHvSet = std_numpy_hvSet/(math.sqrt(len(hvSetPerRun)))
            if debug:
                print("Dev std I: ", std_numpy_I)
                print("Mean error I: ", errAvI)

            #Create canvas for given I(HV) run
            #c = ROOT.TCanvas('c_'+scan[1], 'I(HV)_'+scan[1], 1200, 1200)
            #c.SetGrid()
            xHvSet = array('d')

            #TGraph wants an array on x and y values, fixed values of effective HV
            y = array( 'd' )

            if scan[1] in range(195,198,1):
                x = array( 'd', [6500, 6000, 5500, 5000, 4500, 4000, 3500, 3000, 2500, 2000, 1500, 1000] )
            else:
                x = array( 'd', [6500, 6000, 5500, 5000, 4500, 4000, 3500, 3000, 2500, 2000, 1500, 1000, 500] )
            for i in averageIMon:
                y.append(i)
            
            for i in averageHvSet:
                xHvSet.append(i)

            #Create graph for each run
            grCurrHv.append(ROOT.TGraph(len(averageIMon), x, y))

            grCurrHv[inRun].SetLineColor(2)
            grCurrHv[inRun].SetLineWidth(4)
            grCurrHv[inRun].SetTitle('I(HV)' + scan[1])
            grCurrHv[inRun].SetName('I(HV)' + scan[1])
            grCurrHv[inRun].GetXaxis().SetTitle('HV_{eff} [V]')
            grCurrHv[inRun].GetYaxis().SetTitle('Current density [#muA/cm^{2}]')
            grCurrHv[inRun].GetXaxis().SetLabelFont(62)
            grCurrHv[inRun].GetYaxis().SetLabelFont(62)
            #grCurrHv[inRun].SetMarkerStyle(graphStyle[inRun])
            grCurrHv[inRun].SetMarkerColor(1)
            grCurrHv[inRun].SetMarkerSize(2)

            grCurrHvSet.append(ROOT.TGraph(len(averageIMon), xHvSet, y))

            grCurrHvSet[inRun].SetLineColor(2)
            grCurrHvSet[inRun].SetLineWidth(4)
            grCurrHvSet[inRun].SetTitle('I(HvSet)' + scan[1])
            grCurrHvSet[inRun].SetName('I(HvSet)' + scan[1])
            grCurrHvSet[inRun].GetXaxis().SetTitle('HV_{set} [V]')
            grCurrHvSet[inRun].GetYaxis().SetTitle('Current density [#muA/cm^{2}]')
            grCurrHvSet[inRun].GetXaxis().SetLabelFont(62)
            grCurrHvSet[inRun].GetYaxis().SetLabelFont(62)
            #grCurrHv[inRun].SetMarkerStyle(graphStyle[inRun])
            grCurrHvSet[inRun].SetMarkerColor(1)
            grCurrHvSet[inRun].SetMarkerSize(2)

            if inRun == 0:
                c1.cd()
                grCurrHv[inRun].Draw("AP")
                c1.Update()
                #c16.cd()
                #grCurrHvSet[inRun].Draw("AP")
                #c16.Update()
            else:
                c1.cd()
                grCurrHv[inRun].Draw("SAME P")
                c1.Update()
                #c16.cd()
                #grCurrHvSet[inRun].Draw("AP")
                #c16.Update()

            lCurr.AddEntry(grCurrHv[inRun],scan[1] + "-" + timeIn + "-" + str(round(avgTemp, 2)),"p")

            inRun+=1

            yIHvTime.append(y[hvNumber]) #to take data at 3000 V
            timeInConverted = ROOT.TDatime(scan[2]).Convert()
            xIHvTimeIn.append(timeInConverted)

            yITemperature.append(y[hvNumber])
            dicCurrent[iRun+1] = y[hvNumber]
            dicHvSet[iRun+1] = averageHvSet[hvNumber]


    print(dicCurrent)

    for j in range(len(averageT)):
        xITemperature.append(averageT[j])
        errorsTemperature.append(errAvT)

    currNormalized = array('d')

    for j in range(len(yITemperature)):
        errorsIMon.append(errAvI)
    

    c1.cd()
    lCurr.Draw("SAME")
    c1.Update()
    #c1.Print("I(HV)_@_2000V.png")

    c4.cd()
    #print("Len di xITemperature: ", len(xITemperature), "Len di yITemperature: ", len(yITemperature), "Len di errorsTemperature: ", len(errorsTemperature), "Len di errorsIMon: ", len(errorsIMon))
    #print("xITemperature: ", xITemperature, "yITemperature: ", yITemperature, "errorsTemperature: ", errorsTemperature, "errorsIMon: ", errorsIMon)
    #fitLin = ROOT.TF1("fitLin","[0]+[1]*x",20,26)

    #Test to use temperature of the previous run
    tempPrevRun = array('d')
    for i in range(len(tempNormalized)):
        if i == 0:
            tempPrevRun.append(tempNormalized[0])
        elif i == 1:
            tempPrevRun.append(tempNormalized[1])
        else:
            tempPrevRun.append(tempNormalized[i-1])
    
    fitExp = ROOT.TF1("fitExp","[0]*TMath::Exp([1]*x)",-5,5)

    grCurrTemperature = ROOT.TGraphErrors(len(averageT), tempNormalized, yITemperature, errorsTemperature, errorsIMon)
    #grCurrTemperature = ROOT.TGraphErrors(len(averageT), tempPrevRun, yITemperature, errorsTemperature, errorsIMon)
    zeroValue = grCurrTemperature.Eval(0)
    fitExp.SetParLimits(0,zeroValue-0.1*zeroValue, zeroValue+0.1*zeroValue)
    grCurrTemperature.Fit(fitExp,"MR+")
    q = fitExp.GetParameter(0)
    sigma_q = fitExp.GetParError(0)
    m = fitExp.GetParameter(1)
    sigma_m = fitExp.GetParError(1)
    ROOT.gStyle.SetOptFit(1011)
    grCurrTemperature.SetLineColor(2)
    grCurrTemperature.SetLineWidth(4)
    grCurrTemperature.SetTitle('I(T)')
    grCurrTemperature.SetName('I(T)')
    grCurrTemperature.GetXaxis().SetTitle('Temperature [#circC]')
    grCurrTemperature.GetYaxis().SetTitle('Current [#muA]')
    grCurrTemperature.GetXaxis().SetLabelFont(62)
    grCurrTemperature.GetYaxis().SetLabelFont(62)
    grCurrTemperature.SetMarkerStyle(8)
    grCurrTemperature.SetMarkerColor(1)
    grCurrTemperature.SetMarkerSize(2)
    grCurrTemperature.Draw("AP")
    c4.Update()
    #c4.Print("I(T)_@_2000V.png")

    for j in range(len(yITemperature)):
        myCurrExp = ROOT.TMath.Exp(m*tempNormalized[j])
        currNormalized.append(yITemperature[j]/(myCurrExp))

    grTemperatureTime = ROOT.TGraph(len(averageT), xIHvTimeIn, xITemperature)
    grTemperatureTime.SetLineColor(2)
    grTemperatureTime.SetLineWidth(4)
    grTemperatureTime.SetTitle('')
    grTemperatureTime.SetName('T(t)')
    grTemperatureTime.GetXaxis().SetTitle('time')
    grTemperatureTime.GetYaxis().SetTitle('Temperature [#circC]')
    grTemperatureTime.GetXaxis().SetLabelFont(62)
    grTemperatureTime.GetYaxis().SetLabelFont(62)
    grTemperatureTime.GetXaxis().SetTitleFont(62)
    grTemperatureTime.GetYaxis().SetTitleFont(62)
    grTemperatureTime.GetXaxis().SetTitleSize(0.05)
    grTemperatureTime.GetYaxis().SetTitleSize(0.05)
    grTemperatureTime.GetXaxis().SetLabelSize(0.05)
    grTemperatureTime.GetYaxis().SetLabelSize(0.05)
    grTemperatureTime.SetMarkerStyle(8)
    grTemperatureTime.SetMarkerColor(ROOT.kSpring)
    grTemperatureTime.SetMarkerSize(2)
    grTemperatureTime.GetXaxis().SetTimeDisplay(1)
    grTemperatureTime.GetXaxis().SetTimeOffset(0)
    grTemperatureTime.GetXaxis().SetNdivisions(509)
    grTemperatureTime.GetXaxis().SetTimeFormat("%m-%d %H:%M")
    

    grCurrTime = ROOT.TGraph(len(xIHvTimeIn), xIHvTimeIn, yITemperature)
    grCurrTime.SetLineColor(2)
    grCurrTime.SetLineWidth(4)
    grCurrTime.SetTitle('')
    grCurrTime.SetName('I(t)')
    grCurrTime.GetXaxis().SetTitle('time')
    grCurrTime.GetYaxis().SetTitle('Current [#muA]')
    grCurrTime.GetXaxis().SetLabelFont(62)
    grCurrTime.GetYaxis().SetLabelFont(62)
    grCurrTime.GetXaxis().SetTitleFont(62)
    grCurrTime.GetYaxis().SetTitleFont(62)
    grCurrTime.GetXaxis().SetTitleSize(0.05)
    grCurrTime.GetYaxis().SetTitleSize(0.05)
    grCurrTime.GetXaxis().SetLabelSize(0.05)
    grCurrTime.GetYaxis().SetLabelSize(0.05)
    grCurrTime.GetXaxis().CenterTitle(True)
    grCurrTime.GetYaxis().CenterTitle(True)
    grCurrTime.SetMarkerStyle(8)
    grCurrTime.SetMarkerColor(ROOT.kAzure)
    grCurrTime.SetMarkerSize(2)
    grCurrTime.GetXaxis().SetTimeDisplay(1)
    grCurrTime.GetXaxis().SetTimeOffset(0)
    grCurrTime.GetXaxis().SetNdivisions(509)
    grCurrTime.GetXaxis().SetTimeFormat("%m-%d %H:%M")
    minCurr = grCurrTime.GetHistogram().GetMinimum()
    maxCurr = grCurrTime.GetHistogram().GetMaximum()
    grCurrTime.GetYaxis().SetRangeUser(minCurr,maxCurr)

    grCurrTimeNorm = ROOT.TGraph(len(xIHvTimeIn), xIHvTimeIn, currNormalized)
    grCurrTimeNorm.SetLineColor(2)
    grCurrTimeNorm.SetLineWidth(4)
    grCurrTimeNorm.SetTitle('')
    grCurrTimeNorm.SetName('I(t)')
    grCurrTimeNorm.GetXaxis().SetTitle('time')
    grCurrTimeNorm.GetYaxis().SetTitle('Norm current [#muA]')
    grCurrTimeNorm.GetXaxis().SetLabelFont(62)
    grCurrTimeNorm.GetYaxis().SetLabelFont(62)
    grCurrTimeNorm.GetXaxis().SetTitleFont(62)
    grCurrTimeNorm.GetYaxis().SetTitleFont(62)
    grCurrTimeNorm.GetXaxis().SetTitleSize(0.05)
    grCurrTimeNorm.GetYaxis().SetTitleSize(0.05)
    grCurrTimeNorm.GetXaxis().SetLabelSize(0.05)
    grCurrTimeNorm.GetYaxis().SetLabelSize(0.05)
    grCurrTimeNorm.GetXaxis().CenterTitle(True)
    grCurrTimeNorm.GetYaxis().CenterTitle(True)
    grCurrTimeNorm.SetMarkerStyle(8)
    grCurrTimeNorm.SetMarkerColor(ROOT.kRed)
    grCurrTimeNorm.SetMarkerSize(2)
    grCurrTimeNorm.GetXaxis().SetTimeDisplay(1)
    grCurrTimeNorm.GetXaxis().SetTimeOffset(0)
    grCurrTimeNorm.GetXaxis().SetNdivisions(509)
    grCurrTimeNorm.GetXaxis().SetTimeFormat("%m-%d %H:%M")
    grCurrTimeNorm.GetYaxis().SetRangeUser(minCurr,maxCurr)

    c3.cd(1)
    ROOT.gPad.SetTopMargin(0.02)
    grTemperatureTime.Draw("AP")
    c3.cd(2)
    ROOT.gPad.SetTopMargin(0.02)
    grCurrTime.Draw("AP")
    c3.cd(3)
    ROOT.gPad.SetTopMargin(0.02)
    grCurrTimeNorm.Draw("AP")
    c3.Update()

    grPressureTime = ROOT.TGraph(len(pressureLab), xIHvTimeIn, pressureLab)
    grPressureTime.SetLineColor(2)
    grPressureTime.SetLineWidth(4)
    grPressureTime.SetTitle('')
    grPressureTime.SetName('T(t)')
    grPressureTime.GetXaxis().SetTitle('time')
    grPressureTime.GetYaxis().SetTitle('Pressure [mbar]')
    grPressureTime.GetXaxis().SetLabelFont(62)
    grPressureTime.GetYaxis().SetLabelFont(62)
    grPressureTime.GetXaxis().SetTitleFont(62)
    grPressureTime.GetYaxis().SetTitleFont(62)
    grPressureTime.GetXaxis().SetTitleSize(0.05)
    grPressureTime.GetYaxis().SetTitleSize(0.05)
    grPressureTime.GetXaxis().SetLabelSize(0.05)
    grPressureTime.GetYaxis().SetLabelSize(0.05)
    grPressureTime.SetMarkerStyle(8)
    grPressureTime.SetMarkerColor(ROOT.kSpring)
    grPressureTime.SetMarkerSize(2)
    grPressureTime.GetXaxis().SetTimeDisplay(1)
    grPressureTime.GetXaxis().SetTimeOffset(0)
    grPressureTime.GetXaxis().SetNdivisions(509)
    grPressureTime.GetXaxis().SetTimeFormat("%m-%d %H:%M")

    c28.cd(1)
    ROOT.gPad.SetTopMargin(0.02)
    grPressureTime.Draw("AP")
    c28.cd(2)
    ROOT.gPad.SetTopMargin(0.02)
    grCurrTime.Draw("AP")
    c28.cd(3)
    ROOT.gPad.SetTopMargin(0.02)
    grCurrTimeNorm.Draw("AP")
    c28.Update()

    #c3.Print("I(t)andT(t)_@_2000V.png")


    c2.cd()
    grCurrTime.Draw("AP")
    xCoord = ctypes.c_double(0)
    yCoord = ctypes.c_double(0)
    for i in range(grCurrTime.GetN()):
        grCurrTime.GetPoint(i, xCoord, yCoord)
        x = xCoord.value
        y = yCoord.value
        #print("yCoord: ", type(yCoord))
        if i%2==1:
            l1.append(ROOT.TLatex(x, y+1, "T = "+ str(round(averageT[i], 2))))
        else:
            l1.append(ROOT.TLatex(x, y-1, "T = "+ str(round(averageT[i], 2))))
        l1[i].SetTextSize(0.025)
        l1[i].SetTextFont(42)
        l1[i].SetTextAlign(21)
        l1[i].Draw("SAME")
        c2.Update()

    c2.Update()

    c27 = ROOT.TCanvas('c27', 'I(P)', 1200, 1200)
    c27.SetGrid()
    c27.cd()

    grCurrPress = ROOT.TGraph(len(pressureLab), pressureLab, currNormalized)

    grCurrPress.SetLineColor(2)
    grCurrPress.SetLineWidth(4)
    grCurrPress.SetTitle('I(P)')
    grCurrPress.SetName('I(P)')
    grCurrPress.GetXaxis().SetTitle('Pressure [mbar]')
    grCurrPress.GetYaxis().SetTitle('Current [#muA]')
    grCurrPress.GetXaxis().SetLabelFont(62)
    grCurrPress.GetYaxis().SetLabelFont(62)
    grCurrPress.SetMarkerStyle(8)
    grCurrPress.SetMarkerColor(1)
    grCurrPress.SetMarkerSize(2)
    grCurrPress.Draw("AP")
    c27.Update()
    #c2.Print("I(t)_@_2000V.png")

    # os.chdir('/home/pcald32/rawDataHumi/rootOut')
    c5.cd()
    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    c6 = ROOT.TCanvas('c6', 'Rates1', 1200, 1200)
    c6.Divide(4,2)
    c7 = ROOT.TCanvas('c7', 'Rates2', 1200, 1200)
    c7.Divide(4,2)
    c8 = ROOT.TCanvas('c8', 'Rates3', 1200, 1200)
    c8.Divide(4,2)
    c9 = ROOT.TCanvas('c9', 'Rates4', 1200, 1200)
    c9.Divide(4,2)
    c10 = ROOT.TCanvas('c10', 'Rates5', 1200, 1200)
    c10.Divide(4,2)
    c11 = ROOT.TCanvas('c11', 'Rates6', 1200, 1200)
    c11.Divide(4,2)
    c12 = ROOT.TCanvas('c12', 'Rates7', 1200, 1200)
    c12.Divide(4,2)
    c13 = ROOT.TCanvas('c13', 'Rates8', 1200, 1200)
    c13.Divide(4,2)
    #c6.cd()
    
    histo2D = ROOT.TH2F()
    #print("Tempi non convertiti per titolo: ", dateList)
    maxRate = []
    dateList = []
    averageTemperatureList = []
    averageCurrentList = []
    averageCurrentArray = array('d')
    totCounts = array('d')
    totCountsDivCurr = array('d')
    totCountsList = []
    errRes = []
    errRes1 = []
    errRes2 = []
    totScalerCountsX = []
    totScalerCountsXArray = array('d')
    totScalerCountsY = []
    totScalerCountsYArray = array('d')
    singleStripYRateList = [[] for i in range(24)]
    singleStripXRateList = [[] for i in range(24)]
    numRunInStripY = []

    for k in range(len(HVeff)):
        if HVeff[k] == hv and Triggers[k] != 0 and int(bin[k]) != 0:
            nbin = int(bin[k])
            runNumber = int(runNum[k])
            if runNumber in dicDateTime:
                dateList.append(dicDateTime[runNumber])
                averageTemperatureList.append(dicTemperature[runNumber])
                averageCurrentList.append(dicCurrent[runNumber])
                resistanceList.append(dicHvSet[runNumber]/(dicCurrent[runNumber]*(10**(-6))))
                errRes1.append(((errAvHvSet)/(dicCurrent[runNumber]*(10**(-6))))**2)
                errRes2.append(((dicHvSet[runNumber]*errAvI)/((dicCurrent[runNumber]*(10**(-6)))**2))**2)
                errRes.append(math.sqrt((((errAvHvSet)/(dicCurrent[runNumber]*(10**(-6))))**2) + (((dicHvSet[runNumber]*errAvI)/((dicCurrent[runNumber]*(10**(-6)))**2))**2)))
                print("dizionario correnti a nRun: ", dicCurrent[runNumber])
                f = ROOT.TFile("/home/pcald32/rawDataHumi/rootOut/autotrigger_"+str(nbin)+"_tst1_"+str(hv)+"V.root")
                print("Sto aprendo il file: ", f)
                c5 = f.Get("tst1_column1_rates_xy_2D")
                histo2D = c5.GetListOfPrimitives().FindObject("test1col1_2D")
                maxRate.append(histo2D.GetMaximum())
                histo2D.SetMaximum(1000)
                histos2D.append(histo2D)
                #histo2D.Draw("COLZ")
                #c6.Update()

                g = ROOT.TFile("/home/pcald32/rawDataHumi/root/"+str(nbin)+".root","OPEN") #file root di input
                print("Sto aprendo il file: ", g) 
                histoCounts = g.Get("hTST1") #prende histo conteggi
                integralHistoCounts = histoCounts.Integral()
                totCountsList.append(integralHistoCounts)
                totCounts.append(histoCounts.Integral()) #append integrale del plot
                totCountsDivCurr.append((histoCounts.Integral())/dicCurrent[runNumber])
                xHistoCounts = g.Get("hScTst1x") #prende histo conteggi x scaler
                yHistoCounts = g.Get("hScTst1y") #prende histo conteggi y scaler
                partialScalerX = 0
                partialScalerY = 0
                singleScalerX = array('d')
                singleScalerY = array('d')
                numRunInStripY.append(runNumber)
                with open("/home/pcald32/rawDataHumi/scalersOut/run_"+str(nbin)+"_scalers.out") as timeScalers:
                    lineScalerFile = timeScalers.readlines()
                    print("reading scalersOut: ", lineScalerFile)
                    deltaTimeScaler = 5*(int(lineScalerFile[1]) - int(lineScalerFile[0]))/1000000
                #for binY in range(0,32,1):
                for binY in range(1,yHistoCounts.GetNbinsX()+1,1):
                    numBinY = yHistoCounts.GetBinContent(binY)
                    if binY <= 24:
                        partialScalerY += numBinY/(4.41*deltaTimeScaler)
                        singleScalerY.append(numBinY/(100*deltaTimeScaler*24))
                        singleStripYRateList[binY-1].append(numBinY/(100*deltaTimeScaler))
                    else:
                        partialScalerX += numBinY/(4.41*deltaTimeScaler)
                        singleScalerX.append(numBinY/(100*deltaTimeScaler*24))
                        singleStripXRateList[binY-25].append(numBinY/(100*deltaTimeScaler))
                
                for binX in range(1,17,1):
                    numBinX = xHistoCounts.GetBinContent(binX)
                    partialScalerX += numBinX/(4.41*deltaTimeScaler)
                    singleScalerX.append(numBinX/(100*deltaTimeScaler*24))
                    singleStripXRateList[binX-1+8].append(numBinX/(100*deltaTimeScaler))
                
                print("deltaTimeScaler: ", deltaTimeScaler)
                totScalerCountsY.append(partialScalerY)
                totScalerCountsYArray.append(partialScalerY)
                totScalerCountsX.append(partialScalerX)  
                totScalerCountsXArray.append(partialScalerX)
        else:
            continue
        nbin += 14
        

    #print("Lista di liste: ", singleStripYRateList)
    #print("dimesione array totScalerCountsY: ", len(totScalerCountsY), "elementi contenuti: ", totScalerCountsY)
    #print("dimesione array totScalerCountsX: ", len(totScalerCountsX), "elementi contenuti: ", totScalerCountsX)

    #print("errRes1: ", errRes1)
    #print("errRes2: ", errRes2)

    #print("Lista rate max: ", maxRate)
    maxRateTot = array('d')

    for i in range(len(maxRate)):
        maxRateTot.append(maxRate[i])
    
    for i in range(len(averageTemperatureList)):
        xRTemperature.append(averageTemperatureList[i])
        xRTemperatureNorm.append(averageTemperatureList[i] - 20) #temp normalized to 20°C

    for i in range(len(resistanceList)):
        resistanceArray.append(resistanceList[i]) 

    for i in range(len(averageCurrentList)):
        averageCurrentArray.append(averageCurrentList[i]) 

    for i in range(len(errRes)):
        errResistance.append(errRes[i])
    
    
    c14 = ROOT.TCanvas('c14', 'Rates(T)', 1200, 1200)
    c14.cd()
    #print("Len di xITemperature: ", len(xITemperature), "Len di yITemperature: ", len(yITemperature), "Len di errorsTemperature: ", len(errorsTemperature), "Len di errorsIMon: ", len(errorsIMon))
    #print("xITemperature: ", xITemperature, "yITemperature: ", yITemperature, "errorsTemperature: ", errorsTemperature, "errorsIMon: ", errorsIMon)
    grRatesTemperature = ROOT.TGraph(len(maxRate), xRTemperature, maxRateTot)

    grRatesTemperature.SetLineColor(2)
    grRatesTemperature.SetLineWidth(4)
    grRatesTemperature.SetTitle('rate max (T)')
    grRatesTemperature.SetName('rate max (T)')
    grRatesTemperature.GetXaxis().SetTitle('Temperature [#circC]')
    grRatesTemperature.GetYaxis().SetTitle('Rate [Hz/cm^{2}]')
    grRatesTemperature.GetXaxis().SetLabelFont(62)
    grRatesTemperature.GetYaxis().SetLabelFont(62)
    grRatesTemperature.SetMarkerStyle(8)
    grRatesTemperature.SetMarkerColor(1)
    grRatesTemperature.SetMarkerSize(2)
    grRatesTemperature.Draw("AP")
    c14.Update()
    #c14.SaveAs("Rate(T)_@_2000V.png")


    c15 = ROOT.TCanvas('c15', 'Tot counts (T)', 1200, 1200)
    c15.cd()
    grCountsTemperature = ROOT.TGraph(len(maxRate), xRTemperature, totCounts)

    grCountsTemperature.SetLineColor(2)
    grCountsTemperature.SetLineWidth(4)
    grCountsTemperature.SetTitle('Tot counts (T)')
    grCountsTemperature.SetName('Tot counts (T)')
    grCountsTemperature.GetXaxis().SetTitle('Temperature [#circC]')
    grCountsTemperature.GetYaxis().SetTitle('Counts')
    grCountsTemperature.GetXaxis().SetLabelFont(62)
    grCountsTemperature.GetYaxis().SetLabelFont(62)
    grCountsTemperature.SetMarkerStyle(8)
    grCountsTemperature.SetMarkerColor(1)
    grCountsTemperature.SetMarkerSize(2)
    grCountsTemperature.Draw("AP")
    c15.Update()
    #c15.SaveAs("Rate(T)_@_2000V.png")

    c17 = ROOT.TCanvas('c17', 'Tot counts (t)', 1200, 1200)
    c17.cd()
    grTotCountsTime = ROOT.TGraph(len(xRTemperature), xRTemperature, totCounts)

    grTotCountsTime.SetLineColor(2)
    grTotCountsTime.SetLineWidth(4)
    grTotCountsTime.SetTitle('I(t)')
    grTotCountsTime.SetName('I(t)')
    grTotCountsTime.GetXaxis().SetTitle('time')
    grTotCountsTime.GetYaxis().SetTitle('Counts')
    grTotCountsTime.GetXaxis().SetLabelFont(62)
    grTotCountsTime.GetYaxis().SetLabelFont(62)
    grTotCountsTime.SetMarkerStyle(8)
    grTotCountsTime.SetMarkerColor(1)
    grTotCountsTime.SetMarkerSize(2)
    grTotCountsTime.GetXaxis().SetTimeDisplay(1)
    grTotCountsTime.GetXaxis().SetTimeOffset(0)
    grTotCountsTime.GetXaxis().SetNdivisions(509)
    grTotCountsTime.GetXaxis().SetTimeFormat("%m-%d %H:%M")
    grTotCountsTime.Draw("AP")
    c17.Update()
    
    
    c18 = ROOT.TCanvas('c18', 'Resistance(T)', 1200, 1200)
    c18.cd()
    #print("Len di xITemperature: ", len(xITemperature), "Len di yITemperature: ", len(yITemperature), "Len di errorsTemperature: ", len(errorsTemperature), "Len di errorsIMon: ", len(errorsIMon))
    #print("xITemperature: ", xITemperature, "yITemperature: ", yITemperature, "errorsTemperature: ", errorsTemperature, "errorsIMon: ", errorsIMon)
    #Original
    #grResistanceTemperature = ROOT.TGraphErrors(len(xRTemperature), xRTemperature, resistanceArray, errorsTemperature, errResistance)
    #Normalized to 20°C
    grResistanceTemperature = ROOT.TGraphErrors(len(xRTemperature), xRTemperatureNorm, resistanceArray, errorsTemperature, errResistance)

    grResistanceTemperature.SetLineColor(2)
    grResistanceTemperature.SetLineWidth(4)
    grResistanceTemperature.SetTitle('Resistance (T)')
    grResistanceTemperature.SetName('Resistance (T)')
    grResistanceTemperature.GetXaxis().SetTitle('Temperature [#circC]')
    grResistanceTemperature.GetYaxis().SetTitle('Resistance [#Omega]')
    grResistanceTemperature.GetXaxis().SetLabelFont(62)
    grResistanceTemperature.GetYaxis().SetLabelFont(62)
    grResistanceTemperature.SetMarkerStyle(8)
    grResistanceTemperature.SetMarkerColor(1)
    grResistanceTemperature.SetMarkerSize(2)
    grResistanceTemperature.Draw("AP")
    c18.Update()
    c18.Print("Resistance(T)_@_2000V.png")
    

    c19 = ROOT.TCanvas('c19', 'Div(T)', 1200, 1200)
    c19.cd()

    grTotCountsDivCurrTime = ROOT.TGraph(len(xRTemperature), xRTemperature, totCountsDivCurr)

    grTotCountsDivCurrTime.SetLineColor(2)
    grTotCountsDivCurrTime.SetLineWidth(4)
    grTotCountsDivCurrTime.SetTitle('totCounts/I(t)')
    grTotCountsDivCurrTime.SetName('totCounts/I(t)')
    grTotCountsDivCurrTime.GetXaxis().SetTitle('time')
    grTotCountsDivCurrTime.GetYaxis().SetTitle('totCounts/I')
    grTotCountsDivCurrTime.GetXaxis().SetLabelFont(62)
    grTotCountsDivCurrTime.GetYaxis().SetLabelFont(62)
    grTotCountsDivCurrTime.SetMarkerStyle(8)
    grTotCountsDivCurrTime.SetMarkerColor(1)
    grTotCountsDivCurrTime.SetMarkerSize(2)
    grTotCountsDivCurrTime.GetXaxis().SetTimeDisplay(1)
    grTotCountsDivCurrTime.GetXaxis().SetTimeOffset(0)
    grTotCountsDivCurrTime.GetXaxis().SetNdivisions(509)
    grTotCountsDivCurrTime.GetXaxis().SetTimeFormat("%m-%d %H:%M")
    grTotCountsDivCurrTime.Draw("AP")
    c19.Update()

    c20 = ROOT.TCanvas('c20', 'Tot counts (I)', 1200, 1200)
    c20.cd()
    grTotCountsCurr = ROOT.TGraph(len(averageCurrentArray), averageCurrentArray, totCounts)

    grTotCountsCurr.SetLineColor(2)
    grTotCountsCurr.SetLineWidth(4)
    grTotCountsCurr.SetTitle('I(counts)')
    grTotCountsCurr.SetName('I(counts)')
    grTotCountsCurr.GetXaxis().SetTitle('I')
    grTotCountsCurr.GetYaxis().SetTitle('Counts')
    grTotCountsCurr.GetXaxis().SetLabelFont(62)
    grTotCountsCurr.GetYaxis().SetLabelFont(62)
    grTotCountsCurr.SetMarkerStyle(8)
    grTotCountsCurr.SetMarkerColor(1)
    grTotCountsCurr.SetMarkerSize(2)
    grTotCountsCurr.Draw("AP")
    c20.Update()

    c21 = ROOT.TCanvas('c21', 'scalers x (rate max)', 1200, 1200)
    c21.cd()
    grScalerRateX = ROOT.TGraph(len(totScalerCountsXArray), maxRateTot, totScalerCountsXArray)

    grScalerRateX.SetLineColor(2)
    grScalerRateX.SetLineWidth(4)
    grScalerRateX.SetTitle('scalersX(rateMax)')
    grScalerRateX.SetName('scalersX(rateMax)')
    grScalerRateX.GetXaxis().SetTitle('Rate max Hz/cm^{2}')
    grScalerRateX.GetYaxis().SetTitle('Scaler X Hz/cm^{2}')
    grScalerRateX.GetXaxis().SetLabelFont(62)
    grScalerRateX.GetYaxis().SetLabelFont(62)
    grScalerRateX.SetMarkerStyle(8)
    grScalerRateX.SetMarkerColor(1)
    grScalerRateX.SetMarkerSize(2)
    grScalerRateX.Draw("AP")

    xCoordStripX = ctypes.c_double(0)
    yCoordStripX = ctypes.c_double(0)
    for k in range(grScalerRateX.GetN()):
        grScalerRateX.GetPoint(k, xCoordStripX, yCoordStripX)
        x = xCoordStripX.value
        y = yCoordStripX.value
        #print("yCoord: ", type(yCoord))
        if k%2==1:
            l3.append(ROOT.TLatex(x, y+0.07, str(numRunInStripY[k])))
        else:
            l3.append(ROOT.TLatex(x, y-0.07, str(numRunInStripY[k])))
        l3[k].SetTextSize(0.025)
        l3[k].SetTextFont(42)
        l3[k].SetTextAlign(21)
        l3[k].Draw("SAME")
        c21.Update()
    
    c21.Update()

    c22 = ROOT.TCanvas('c22', 'scalers y (rate max)', 1200, 1200)
    c22.cd()
    grScalerRateY = ROOT.TGraph(len(totScalerCountsYArray), maxRateTot, totScalerCountsYArray)

    grScalerRateY.SetLineColor(2)
    grScalerRateY.SetLineWidth(4)
    grScalerRateY.SetTitle('scalersY(rateMax)')
    grScalerRateY.SetName('scalersY(rateMax)')
    grScalerRateY.GetXaxis().SetTitle('Rate max Hz/cm^{2}')
    grScalerRateY.GetYaxis().SetTitle('Scaler Y Hz/cm^{2}')
    grScalerRateY.GetXaxis().SetLabelFont(62)
    grScalerRateY.GetYaxis().SetLabelFont(62)
    grScalerRateY.SetMarkerStyle(8)
    grScalerRateY.SetMarkerColor(1)
    grScalerRateY.SetMarkerSize(2)
    grScalerRateY.Draw("AP")
   

    xCoordStripY = ctypes.c_double(0)
    yCoordStripY = ctypes.c_double(0)
    for k in range(grScalerRateY.GetN()):
        grScalerRateY.GetPoint(k, xCoordStripY, yCoordStripY)
        x = xCoordStripY.value
        y = yCoordStripY.value
        #print("yCoord: ", type(yCoord))
        if k%2==1:
            l2.append(ROOT.TLatex(x, y+0.05, str(numRunInStripY[k])))
        else:
            l2.append(ROOT.TLatex(x, y-0.05, str(numRunInStripY[k])))
        l2[k].SetTextSize(0.025)
        l2[k].SetTextFont(42)
        l2[k].SetTextAlign(21)
        l2[k].Draw("SAME")
        c22.Update()

    c22.Update()


    
    c23 = ROOT.TCanvas('c23', 'scalers y (rate max)', 1200, 1200)
    c23.cd()
    c23.Divide(4,3)
    c24 = ROOT.TCanvas('c24', 'scalers y (rate max) 2', 1200, 1200)
    c24.cd()
    c24.Divide(4,3)
    grSingleStripRateY = list()
    for i, strip in enumerate(singleStripYRateList):
        grSingleStripRateY.append(ROOT.TGraph(len(strip), maxRateTot, array("d",strip)))
        grSingleStripRateY[i].SetLineColor(2)
        grSingleStripRateY[i].SetLineWidth(4)
        grSingleStripRateY[i].SetTitle('Strip Y: '+str(i+1))
        grSingleStripRateY[i].SetName('Strip Y: '+str(i+1))
        grSingleStripRateY[i].GetXaxis().SetTitle('Rate max Hz/cm^{2}')
        grSingleStripRateY[i].GetYaxis().SetTitle('Rate Strip Y Hz/cm^{2}')
        grSingleStripRateY[i].GetXaxis().SetLabelFont(62)
        grSingleStripRateY[i].GetYaxis().SetLabelFont(62)
        grSingleStripRateY[i].SetMarkerStyle(8)
        grSingleStripRateY[i].SetMarkerColor(1)
        grSingleStripRateY[i].SetMarkerSize(2)
        if i < 12:
            c23.cd(i+1)
            grSingleStripRateY[i].Draw("AP")
            c23.Update()
        else:
            c24.cd(i-11)
            grSingleStripRateY[i].Draw("AP")
            c24.Update()
   
        
    c25 = ROOT.TCanvas('c25', 'scalers x (rate max)', 1200, 1200)
    c25.cd()
    c25.Divide(4,3)
    c26 = ROOT.TCanvas('c26', 'scalers x (rate max) 2', 1200, 1200)
    c26.cd()
    c26.Divide(4,3)
    grSingleStripRateX = list()
 
    for i, strip in enumerate(singleStripXRateList):
        print("i",i)
        grSingleStripRateX.append(ROOT.TGraph(len(strip), maxRateTot, array("d",strip)))
        grSingleStripRateX[i].SetLineColor(2)
        grSingleStripRateX[i].SetLineWidth(4)
        grSingleStripRateX[i].SetTitle('Strip X: '+str(i+1))
        grSingleStripRateX[i].SetName('Strip X: '+str(i+1))
        grSingleStripRateX[i].GetXaxis().SetTitle('Rate max Hz/cm^{2}')
        grSingleStripRateX[i].GetYaxis().SetTitle('Rate Strip X Hz/cm^{2}')
        grSingleStripRateX[i].GetXaxis().SetLabelFont(62)
        grSingleStripRateX[i].GetYaxis().SetLabelFont(62)
        grSingleStripRateX[i].SetMarkerStyle(8)
        grSingleStripRateX[i].SetMarkerColor(1)
        grSingleStripRateX[i].SetMarkerSize(2)
        if i < 12:
            c25.cd(i+1)
            grSingleStripRateX[i].Draw("AP")
            c25.Update()
        else:
            c26.cd(i-11)
            grSingleStripRateX[i].Draw("AP")
            c26.Update()
    
    """
    c24 = ROOT.TCanvas('c24', 'scalers x (rate max)', 1200, 1200)
    c24.cd()
    c24.Divide(12,2)
    grSingleStripRateX = list()
    for i in range(0,11,1):
        grSingleStripRateX[i].append(ROOT.TGraph(len(singleScalerX), maxRateTot, singleScalerX[i]))
        grSingleStripRateX[i].SetLineColor(2)
        grSingleStripRateX[i].SetLineWidth(4)
        grSingleStripRateX[i].SetTitle('singleStripX(rateMax)')
        grSingleStripRateX[i].SetName('singleStripX(rateMax)')
        grSingleStripRateX[i].GetXaxis().SetTitle('Rate max Hz/cm^{2}')
        grSingleStripRateX[i].GetYaxis().SetTitle('Rate Strip X Hz/cm^{2}')
        grSingleStripRateX[i].GetXaxis().SetLabelFont(62)
        grSingleStripRateX[i].GetYaxis().SetLabelFont(62)
        grSingleStripRateX[i].SetMarkerStyle(8)
        grSingleStripRateX[i].SetMarkerColor(1)
        grSingleStripRateX[i].SetMarkerSize(2)
        c24.cd(i)
        grSingleStripRateX[i].Draw("AP")
        c24.Update()
    
    c25 = ROOT.TCanvas('c25', 'scalers x (rate max) 2', 1200, 1200)
    c25.cd()
    c25.Divide(12,2)
    grSingleStripRateX = list()
    for i in range(0,11,1):
        grSingleStripRateX[i].append(ROOT.TGraph(len(singleScalerX), maxRateTot, singleScalerX[i]))
        grSingleStripRateX[i].SetLineColor(2)
        grSingleStripRateX[i].SetLineWidth(4)
        grSingleStripRateX[i].SetTitle('singleStripX(rateMax)')
        grSingleStripRateX[i].SetName('singleStripX(rateMax)')
        grSingleStripRateX[i].GetXaxis().SetTitle('Rate max Hz/cm^{2}')
        grSingleStripRateX[i].GetYaxis().SetTitle('Rate Strip X Hz/cm^{2}')
        grSingleStripRateX[i].GetXaxis().SetLabelFont(62)
        grSingleStripRateX[i].GetYaxis().SetLabelFont(62)
        grSingleStripRateX[i].SetMarkerStyle(8)
        grSingleStripRateX[i].SetMarkerColor(1)
        grSingleStripRateX[i].SetMarkerSize(2)
        c25.cd(i)
        grSingleStripRateX[i].Draw("AP")
        c25.Update()
    
    """
    
    """
    for nrun in range(7966, 8510, 14):
        if (nrun == 8050 or nrun == 8120 or nrun == 8162 or nrun == 8232 or nrun == 8302):
            continue
        else:
            f = ROOT.TFile("autotrigger_"+str(nrun)+"_tst1_"+str(hv)+"V.root")
            #print("Sto aprendo il file: ", f)
            c5 = f.Get("tst1_column1_rates_xy_2D")
            histo2D = c5.GetListOfPrimitives().FindObject("test1col1_2D")
            histo2D.SetMaximum(1000)
            histos2D.append(histo2D)
            #histo2D.Draw("COLZ")
            #c6.Update()
    """
    print("Len histos2D: ", len(histos2D))
        #print("Tempi non convertiti per titolo: ", dateList)
    print(len(dateList))
        #print("Temperature per titolo: ", averageTemperatureList)
    print(len(averageTemperatureList))
    print("Correnti per titolo: ", averageCurrentList)
    print(len(averageCurrentList))

    for k in range(len(histos2D)):
        print("k: ", k)
        if k < 8:
            c6.cd(k+1)
            histos2D[k].SetTitle(str(dateList[k])+" "+str(round(averageTemperatureList[k],2))+" #circC "+str(round(averageCurrentList[k],2))+" #muA")
            histos2D[k].Draw("COLZ")
            #c6.SetRightMargin(0.04)
            ROOT.gPad.SetRightMargin(0.15)
            ROOT.gPad.SetLogz()
            c6.Update()
        elif (k > 7 and k < 16):
            c7.cd(k-7)
            histos2D[k].SetTitle(str(dateList[k])+" "+str(round(averageTemperatureList[k],2))+" #circC "+str(round(averageCurrentList[k],2))+" #muA")
            histos2D[k].Draw("COLZ")
            ROOT.gPad.SetRightMargin(0.15)
            ROOT.gPad.SetLogz()
            c7.Update()
        elif (k > 15 and k < 24):
            c8.cd(k-15)
            histos2D[k].SetTitle(str(dateList[k])+" "+str(round(averageTemperatureList[k],2))+" #circC "+str(round(averageCurrentList[k],2))+" #muA")
            histos2D[k].Draw("COLZ")
            ROOT.gPad.SetRightMargin(0.15)
            ROOT.gPad.SetLogz()
            c8.Update()
        elif (k > 23 and k < 32):
            c9.cd(k-23)
            histos2D[k].SetTitle(str(dateList[k])+" "+str(round(averageTemperatureList[k],2))+" #circC "+str(round(averageCurrentList[k],2))+" #muA")
            histos2D[k].Draw("COLZ")
            ROOT.gPad.SetRightMargin(0.15)
            ROOT.gPad.SetLogz()
            c9.Update()
        elif (k > 31 and k < 40):
            c10.cd(k-31)
            histos2D[k].SetTitle(str(dateList[k])+" "+str(round(averageTemperatureList[k],2))+" #circC "+str(round(averageCurrentList[k],2))+" #muA")
            histos2D[k].Draw("COLZ")
            ROOT.gPad.SetRightMargin(0.15)
            ROOT.gPad.SetLogz()
            c10.Update()
        elif (k > 39 and k < 48):
            c11.cd(k-39)
            histos2D[k].SetTitle(str(dateList[k])+" "+str(round(averageTemperatureList[k],2))+" #circC "+str(round(averageCurrentList[k],2))+" #muA")
            histos2D[k].Draw("COLZ")
            ROOT.gPad.SetRightMargin(0.15)
            ROOT.gPad.SetLogz()
            c11.Update()
        elif (k > 47 and k < 56):
            c12.cd(k-47)
            histos2D[k].SetTitle(str(dateList[k])+" "+str(round(averageTemperatureList[k],2))+" #circC "+str(round(averageCurrentList[k],2))+" #muA")
            histos2D[k].Draw("COLZ")
            ROOT.gPad.SetRightMargin(0.15)
            ROOT.gPad.SetLogz()
            c12.Update()
        else:
            c13.cd(k-55)
            histos2D[k].SetTitle(str(dateList[k])+" "+str(round(averageTemperatureList[k],2))+" #circC "+str(round(averageCurrentList[k],2))+" #muA")
            histos2D[k].Draw("COLZ")
            ROOT.gPad.SetRightMargin(0.15)
            ROOT.gPad.SetLogz()
            c13.Update()
    os.chdir('/home/pcald32/labStrada/analysis/humidityTest')

    """
    cMult = ROOT.TCanvas('cMult','I(HV) mult', 1200, 1200 )
    cMult.SetGrid()
    cMult.cd()
    mCurrHV.Draw("AP")
    lCurr.Draw("SAME")
    cMult.Update()

    fileOutput.cd()
    cMult.Write("multCurr")
    """
    input("Enter your value: ")
    fileOutput.cd()
    c1.Write('I(HV)')
    c2.Write('I(t)')
    c3.Write('T(t)')
    c4.Write('I(T)')
    fileOutput.Close()

if __name__ == "__main__":
    main()