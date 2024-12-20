import mysql.connector
import numpy as np
import time
import propar
import os
from datetime import datetime
import serial.tools.list_ports #for serial communication 

def main():
    #Communicate with arduino
    ports = serial.tools.list_ports.comports() #returns a list of all com ports
    serialInst = serial.Serial() #create instance of serial port

    portVar = "COM4" #we know the arduino is on COM4 port
    serialInst.baudrate = 9600 #boud rate of arduino
    serialInst.port = portVar #set port
    serialInst.open() #open serial port communication port

    #Send message to arduino to close the interlock since we have gas
    message = "close"
    time.sleep(5)
    serialInst.write(message.encode('utf-8'))
    time.sleep(5)

    counter = 0
    # Communication with the MFC
    master = propar.master('COM3', 38400)

    # Get nodes on the network
    nodes = master.get_nodes()

    os.chdir("flowTrend")

    now = datetime.now()
    
    print("now = ", now)

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    print("date and time =", dt_string)

    f = open("flowTrend"+dt_string+".txt", mode="wt") #open file to write out waveforms
    #[Ar, R134a, i-C4H10, SF6]
    counterInterlock = [0,0,0,0] #list of counters for thr inteerlock (each element = one gas)

    while True:

        print("Alive counter:",counter)

        now = int(time.time())
        
        names = []
        flows=[]
        setPoints=[]
        
        # Read the usertag of all nodes
        for node in nodes:
            user_tag = master.read(node['address'], 113, 6, propar.PP_TYPE_STRING)
            flow =  master.read(node['address'], 33, 0, propar.PP_TYPE_FLOAT)
            setPoint =  master.read(node['address'], 33, 3, propar.PP_TYPE_FLOAT)
            
            names.append(user_tag)
            flows.append(flow)
            setPoints.append(setPoint)

            print(user_tag, ":", flow, "ml/min, setpoint: ",setPoint,"ml/min")

            #Control mode: write value = 0 , Process: 1, Parameter: 4, Type: character
            
        for elem, flow in enumerate(flows):
            print(flow, setPoints[elem])
            print("Nominal flow ",elem,counterInterlock[elem])
            if flow < setPoints[elem]-0.20*setPoints[elem] or flow > setPoints[elem] + 0.20*setPoints[elem]: #flow is above(below) setpoint+(-)20% of setpoint
                counterInterlock[elem] = counterInterlock[elem] + 1
                print("Flow under setpoint ",elem,counterInterlock[elem])
            else:
                counterInterlock[elem] = 0
                print("Flow ok ",elem,counterInterlock[elem])

        if any(ele == 4 for ele in counterInterlock) : #If for four times the gas is outside the desired range (any gas)
            print("Ar ",counterInterlock[0],"R134a ",counterInterlock[1],"i-C4H10 ",counterInterlock[2],"SF6 ",counterInterlock[3])
            #Send open message to Arduino to kill HV
            message = "open"
            time.sleep(5)
            serialInst.write(message.encode('utf-8'))
            time.sleep(5)
            #Stop the gas flow
            for node in nodes:
                #master.write(node['address'],0,1,1,propar.PP_TYPE_INT32)
                master.write(node['address'],33,3,propar.PP_TYPE_FLOAT,0)

        print("\n")

        val = (flows[0],setPoints[0],names[0],flows[1],setPoints[1],names[1],flows[2],setPoints[2],names[2],flows[3],setPoints[3],names[3])

        f.write(str(now) + "\t" + str(flows[1]) + "\t" + str(flows[2]) + "\t" + str(flows[3]) + "\n")
        f.flush()

        counter = counter+1
        time.sleep(5)

if __name__ == "__main__":
    main()