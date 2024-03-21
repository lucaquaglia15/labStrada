from audioop import avg
from operator import le
from pickle import TRUE
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

import sys #To perform system operation
from math import sin
from array import array



def main():
    c5 = ROOT.TCanvas('c5', 'Rate', 1200, 1200)
    #pad1 = ROOT.TPad("pad1","",0,0,1,1)
    #pad1 = ROOT.TGraph("pad1","",0,0,1,1)

    graph = ROOT.TGraph()
    
    os.chdir('/home/pcald32/rawDataHumi/rootOut')
    #with open("autotrigger_8510_tst1_0V.root") as rootOutFile:
        #myTCanvas = ('tst1_column1_rates_xy_2D')
    f = ROOT.TFile("autotrigger_8510_tst1_0V.root")
    graph = f.Get("tst1_column1_rates_xy_2D")
    c5.cd()
    graph.Draw()
    c5.Update()

    #myFile = ROOT.TFile.Open("autotrigger_8510_tst1_0V.root")
    #c5 = myFile.TCanvas
    #c5.GetCanvas()
        #pad1.GetPad(2)
    #c5.cd(1)
    #c5.Draw()
    #c5.cd(1)
    #pad1.Draw()
    #pad1.cd()
    
    #c5.Paint()
    input("Enter your value: ")



if __name__ == "__main__":
    main()