#Python file t get the data from the Arduino and post them to mysql database running on this machine

import mysql.connector #to connect to db to send the data
import serial.tools.list_ports #for serial communication 
from dotenv import dotenv_values

secrets = dotenv_values("/home/pcald32/labStrada/.env")

#Supply voltage to power humidity sensor
Vsupp = 5 #5 Volts

#Communicate with arduino
ports = serial.tools.list_ports.comports() #returns a list of all com ports
serialInst = serial.Serial() #create instance of serial port

portVar = "/dev/ttyUSB0" #Arduino/ESP32 com port
serialInst.baudrate = 9600 #boud rate of arduino
serialInst.port = portVar #set port
serialInst.open() #open serial port communication port

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
        print("Ambient temperature = " + str(split_data[0]) + " °C")
        print("Ambient humidity = " + str(split_data[1]) + " %")
        print("V reading IN = " + str(split_data[2]) + " V")
        print("V reading OUT = " + str(split_data[3]) + " V")

        Tenv = split_data[0] #Ambient temperature
        humiEnv = split_data[1] #Ambient humidity
        Vin = split_data[2] #voltage of input humidity sensor
        Vout = split_data[3] #voltage of output humidity sensor
        
        humiIn = (1/0.062)*((Vin/Vsupp) - 0.16) #Not normalized for temperature
        humiOut = (1/0.062)*((Vout/Vsupp) - 0.16) #Not normalized for temperature

        normHumiIn = humiIn/(1.0546-0.00216*Tenv) #Normalized for temperature
        normHumiOut = humiOut/(1.0546-0.00216*Tenv) #Normalized for temperature

        val = (Tenv,humiEnv,humiIn,normHumiIn,humiOut,normHumiOut) 
        sql = "INSERT INTO humiSens (temperature,ambHumidity,gasInHumi,normGasInHumi,gasOutHumi,normGasOutHumi) VALUES (%s,%s,%s,%s,%s,%s)"
        mycursor.execute(sql, val)

        mydb.commit() #execute query

        print(mycursor.rowcount, "record inserted.") #succesful print out
        
        counter += 1