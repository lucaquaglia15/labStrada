#Quick code to plot efficiency over time

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mysql.connector #to connect to db to send the data
import os  #To create new folders and so on
import ROOT #Root CERN functions
from ROOT import TFile
import time #For functions such as sleep

def getTime(mycursor, run):
    getScanTime = ("SELECT date, endDate FROM efficiencyScan WHERE runNumber = '" + run + "'")
    mycursor.execute(getScanTime)

    time = mycursor.fetchall()
    return time

def main():

    runs = ["418","419","420"] #List of the runs to be analyzed

    #connect to db to fetch time of the runs
    mydb = mysql.connector.connect( #db object on localhost
        host="localhost",
        user="root",
        password="pcald32",
        database="labStrada"
    )

    mycursor = mydb.cursor()

    #Fetch time of the runs
    times = []
    
    for run in runs:
        times.append(getTime(mycursor,run))
    
    startTime = []
    endTime = []
    
    for time in times:
        #print(time[0])
        startTime.append(time[0][0])
        endTime.append(time[0][1])

    print(startTime)
    print(endTime)

    #List to store efficiency values fetched from all runs
    eff = []

    for run in runs:
        inFile = ROOT.TFile.Open("/home/pcald32/runs/efficiencyScans/scan_" + run + "/OutFile_ECOgas_"+ run + ".root","READ")
        canvasEff = inFile.Get("Efficiency_X_" + run)

        gEff = ROOT.TGraphErrors = canvasEff.FindObject("Graph")
        
        for i in range(gEff.GetN()):
            eff.append(gEff.GetPointY(i))


    fig, ax = plt.subplots()             # Create a figure containing a single Axes.
    ax.plot(startTime, eff, marker = 'o', c = 'b')  # Plot some data on the Axes.
    myFmt = mdates.DateFormatter('%d-%m %H:%M:%S')
    plt.xticks(rotation=45,fontsize='x-small')
    ax.xaxis.set_major_formatter(myFmt)
    
    plt.show()    

if __name__ == "__main__":
    main()