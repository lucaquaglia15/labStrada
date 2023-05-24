import mysql.connector #to connect to db to send the data
import time
import os
import asyncio
import telegram
import sys
import datetime #To get date, time and perform operations on them
sys.path.insert(0, '/home/pcald32/labStrada/DAQ/efficiencyScan') #import CAEN.py file from currentScan folder
import constants
sys.path.insert(0, '/home/pcald32/labStrada/DAQ/currentScan') #import CAEN.py file from currentScan folder
from CAEN import CAEN

def killHV():
    hvModule = CAEN(b"90.147.203.174",b"admin",b"admin")
    handle = hvModule.connect()
    slots = []
    slots = constants.slot #HV module slots
    channels = []
    channels = constants.channels #HV channels
    #Set channel name and switch HV on
    for slot in range(len(slots)):
        for iCh, channel in enumerate(channels[slot]):
            hvModule.setParameter(handle,slots[slot],b"Pw",channel,0)
    hvModule.disconnect(handle)

async def main():

    bot = telegram.Bot("5944587331:AAHwccVKeVlouniYjuoZcNMGyGh-_wgALrw")

    mydb = mysql.connector.connect( #db object on localhost
      host="localhost",
      user="root",
      password="pcald32",
      database="labStrada"
    )

    mycursor = mydb.cursor()

    counter = 0 #alive counter

    while True:
        mydb.cmd_refresh(1)
        getLastFlow = ("SELECT date, ch1, sp1, ch2, sp2, ch3, sp3, ch4, sp4 FROM inputFlow ORDER BY date DESC LIMIT 1")
        #getLastFlow = ("SELECT date, ch1, ch2, ch3, ch4 FROM inputFlow ")
        mycursor.execute(getLastFlow)

        lastFlow = mycursor.fetchall()
        #print(lastFlow[0][2])
        lastDate = lastFlow[0][0]
        delta = (datetime.datetime.now() - lastDate).total_seconds() #Calculate difference between now and last measurement in the db

        if delta > 60: #1200 s = logger stopped for more than 20 minutes
            print("MFC flow logging stopped more than 1 minute ago!")
            print("Last flow saved is at:",str(lastDate))
            await bot.send_message(text="---Last flow over one minute ago "+str(lastDate)+" ---", chat_id=-1001902276824)

        if lastFlow[0][1]>(lastFlow[0][2]+0.1*lastFlow[0][2]) or lastFlow[0][1]<(lastFlow[0][2]-0.1*lastFlow[0][2]):
            killHV()
            await bot.send_message(text="---Argon flow outside limits ("+str(lastFlow[0][2])+"), current flow: "+str(lastFlow[0][1])+ "---", chat_id=-1001902276824)
                
        if lastFlow[0][3]>(lastFlow[0][4]+0.1*lastFlow[0][4]) or lastFlow[0][3]<(lastFlow[0][4]-0.1*lastFlow[0][4]):
           killHV()
           await bot.send_message(text="---R134a flow outside limits ("+str(lastFlow[0][4])+"), current flow: "+str(lastFlow[0][3])+ "---", chat_id=-1001902276824)

        if lastFlow[0][5]>(lastFlow[0][6]+0.1*lastFlow[0][6]) or lastFlow[0][5]<(lastFlow[0][6]-0.1*lastFlow[0][6]):
            killHV()
            await bot.send_message(text="---Isobutane flow outside limits ("+str(lastFlow[0][6])+"), current flow: "+str(lastFlow[0][5])+ "---", chat_id=-1001902276824)

        if lastFlow[0][7]>(lastFlow[0][8]+0.1*lastFlow[0][8]) or lastFlow[0][7]<(lastFlow[0][8]-0.1*lastFlow[0][8]):
            killHV()
            await bot.send_message(text="---SF6 flow outside limits ("+str(lastFlow[0][8])+"), current flow: "+str(lastFlow[0][7])+ "---", chat_id=-1001902276824)


        time.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
