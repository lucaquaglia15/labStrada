import mysql.connector
import numpy as np
import time
import propar

mydb = mysql.connector.connect(
    host = "90.147.203.161",
    user = "pcGas",
    password = "pcGas32!",
    database = "labStrada"
)

mycursor = mydb.cursor()

counter = 0
# Create the master
master = propar.master('COM3', 38400)

# Get nodes on the network
nodes = master.get_nodes()

while True:

    print("Alive counter:",counter)
    
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
    
    print("\n")

    val = (flows[0],setPoints[0],names[0],flows[1],setPoints[1],names[1],flows[2],setPoints[2],names[2],flows[3],setPoints[3],names[3])

    sql = "INSERT INTO inputFlow (ch1,sp1,channel1Gas,ch2,sp2,channel2Gas,ch3,sp3,channel3Gas,ch4,sp4,channel4Gas) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    mycursor.execute(sql,val)
    mydb.commit()

    print(mycursor.rowcount,'record inserted')

    counter = counter+1
    time.sleep(30)