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

def main():

    #connects to the dd
    mydb = mysql.connector.connect( #db object on localhost
        host="localhost",
        user="root",
        password="pcald32",
        database="labStrada"
    )

    mycursor = mydb.cursor()

    data = []

    with open("/home/pcald32/rawDataHumi/customtextout.txt") as configFile:
        scanPoints = configFile.readlines()
        #print(scanPoints)

        for point in scanPoints:
            asList = point.split("\t")
            data.append(asList)

    for i in range(len(data)):
        value = [data[i][0]+" "+data[i][1],data[i][2],data[i][3]]
        print(value)
        statement = "INSERT INTO envPar(date,temperature,pressure) VALUES(%s,%s,%s)"
        mycursor.execute(statement, value)
        mydb.commit()

    #print(data)

if __name__ == "__main__":
    main()