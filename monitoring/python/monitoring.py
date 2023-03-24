#Python file t get the data from the Arduino and post them to mysql database running on this machine

import mysql.connector #to connect to db to send the data
import serial.tools.list_ports #for serial communication 
import numpy as np

#Define polynomial for conversion from mV to flow
#coeff = 0.57
p = np.poly1d([3.09333, -7.05143, 5.9581, 0.500571])

#Communicate with arduino
ports = serial.tools.list_ports.comports() #returns a list of all com ports
serialInst = serial.Serial() #create instance of serial port

portVar = "/dev/ttyUSB0" #we know the arduino is on COM4 port
serialInst.baudrate = 9600 #boud rate of arduino
serialInst.port = portVar #set port
serialInst.open() #open serial port communication port

mydb = mysql.connector.connect( #db object on localhost
  host="localhost",
  user="root",
  password="pcald32",
  database="labStrada"
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

        val = (split_data[0],split_data[1],split_data[2])
        sql = "INSERT INTO envPar (temperature, pressure, humidity) VALUES (%s, %s, %s)" #sql query
        mycursor.execute(sql, val)

        mydb.commit() #execute query

        #Flow sensor
        print("V reading = " + str(split_data[3]) + " V")
        
        #Invert calibration function
        p[0] = p[0]-float(split_data[3])
        print(p[0])
        print(p.r)

        airFlow = 0.

        voltage = float(split_data[3])
        for x in p.r:
            if x <= 1 and x >= 0:    
              airFlow = float(x)*60
        realFlow = airFlow/3.33

        #print(voltage)
        #print(airFlow)
        #print(realFlow)

        val = (voltage,airFlow,realFlow)
        sql = "INSERT INTO flow (voltage, airFlow, realFlow) VALUES (%s, %s, %s)" #sql query
        mycursor.execute(sql, val)
        
        mydb.commit() #execute query

        print(mycursor.rowcount, "record inserted.") #succesful print out
        
        counter += 1
        p[0] = 0.500571