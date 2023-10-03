#Python file t get the data from the Arduino and post them to mysql database running on this machine

import mysql.connector #to connect to db to send the data
import serial.tools.list_ports #for serial communication 
import numpy as np
import time
import os
from datetime import datetime

#Communicate with arduino
ports = serial.tools.list_ports.comports() #returns a list of all com ports
serialInst = serial.Serial() #create instance of serial port

portVar = "COM4" #we know the arduino is on COM4 port
serialInst.baudrate = 9600 #boud rate of arduino
serialInst.port = portVar #set port
serialInst.open() #open serial port communication port

#os.chdir("C:\Users\Luca\Documents\temperatureTrend")
os.chdir("temperatureTrend")

now = datetime.now()
 
print("now =", now)

# dd/mm/YY H:M:S
dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
print("date and time =", dt_string)

f = open("tempTest"+dt_string+".txt", mode="wt") #open file to write out waveforms

counter = 0 #alive counter

while True: #infinte loop to listen to data from arduino and post it to db
    if serialInst.in_waiting: #there is data in the buffer
        print("-----alive counter " + str(counter) + " -----")

        now = int(time.time())
        #print(int(now))

        packet = serialInst.readline()
        decodePacket = packet.decode('utf')
        print(packet.decode('utf'))

        split_data = packet.decode('utf').split('x')
        
        #temperature sensor
        print("Temperature = " + str(split_data[0]) + " °C")
        print("Pressure = " + str(split_data[1]) + " mbar")
        #print("Humidity = " + str(split_data[2]) + " %")

        temp = str(split_data[0])
        press = str(split_data[1])

        f.write(str(now) + "\t" + temp + "\t" + press)
        f.flush()

        #val = (split_data[0],split_data[1],split_data[2])