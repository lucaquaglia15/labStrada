#Python file t get the data from the Arduino and post them to mysql database running on this machine

import mysql.connector #to connect to db to send the data
import serial.tools.list_ports #for serial communication 
import numpy as np
from dotenv import dotenv_values
import math

#Define polynomial for conversion from mV to flow
#coeff = 0.57
#p = np.poly1d([3.09333, -7.05143, 5.9581, 0.500571])

#Communicate with arduino
ports = serial.tools.list_ports.comports() #returns a list of all com ports
serialInst = serial.Serial() #create instance of serial port

portVar = "/dev/ttyUSB0" #we know the arduino is on ttyUSB0 port
serialInst.baudrate = 9600 #boud rate of arduino
serialInst.port = portVar #set port
serialInst.open() #open serial port communication port

secrets = dotenv_values("/home/pcald32/labStrada/.env")

mydb = mysql.connector.connect( #db object on localhost
  host=secrets["host"],
  user=secrets["user"],
  password=secrets["password"],
  database=secrets["database"]
)

mycursor = mydb.cursor()

counter = 0 #alive counter

while True: #infinte loop to listen to data from arduino and post it to db
    if serialInst.in_waiting: #there is data in the buffer

        print("-----alive counter " + str(counter) + " -----")

        packet = serialInst.readline()
        decodePacket = packet.decode('utf')
        print(packet.decode('utf'))

        split_data = packet.decode('utf').split('x')
        
        #temperature sensor
        print("Temperature = " + str(split_data[0]) + " °C")
        print("Pressure = " + str(split_data[1]) + " mbar")
        print("Humidity = " + str(split_data[2]) + " %")

        if math.isnan(float(split_data[0])) or math.isnan(float(split_data[1])) or math.isnan(float(split_data[2])):
          print("nan value found")
          continue
        
        else:
          #val = (split_data[0],split_data[1]) #without humidity
          val = (split_data[0],split_data[1],split_data[2]) #w humi
          #sql = "INSERT INTO envPar (temperature, pressure) VALUES (%s, %s)" #sql query without humidity
          sql = "INSERT INTO envPar (temperature, pressure, humidity) VALUES (%s, %s, %s)" #sql query w humidity
          mycursor.execute(sql, val)

          mydb.commit() #execute query

        """
        #Flow sensor
        #print("V reading = " + str(split_data[3]) + " V")
        print("V reading = " + str(split_data[2]) + " V")
        
        #Invert calibration function
        #p[0] = p[0]-float(split_data[3])
        p[0] = p[0]-float(split_data[2])
        print(p[0])
        print(p.r)

        airFlow = 0.

        #voltage = float(split_data[3])
        voltage = float(split_data[2])
        for x in p.r:
            if x <= 1 and x >= 0:    
              airFlow = float(x)*60
        realFlow = airFlow/3.33

        val = (voltage,airFlow,realFlow)
        sql = "INSERT INTO flow (voltage, airFlow, realFlow) VALUES (%s, %s, %s)" #sql query
        mycursor.execute(sql, val)
        
        mydb.commit() #execute query
        """

        print(mycursor.rowcount, "record inserted.") #succesful print out
        
        counter += 1
        #p[0] = 0.500571
