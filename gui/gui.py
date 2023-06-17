import PySimpleGUI as sg
import mysql.connector #to connect to db to send the data
import psutil
import os
import subprocess

#New mixture window
def newMixture(db,cursor):
    print("Opening new mixture panel")

    sum = 0 #sum of percentages, sanity check

    mixLayout=[
            [sg.Text('Enter new mixture',size=(20, 1), font=('Lucida',12,'bold'),justification='left')],
            [sg.Text('name', size=(15, 1)), sg.InputText(key='name')],
            [sg.Text('HFOze', size=(15, 1)), sg.InputText(key='HFOze',default_text='0')],
            [sg.Text('HFOyf', size=(15, 1)), sg.InputText(key='HFOyf',default_text='0')],
            [sg.Text('R134a', size=(15, 1)), sg.InputText(key='R134a',default_text='0')],
            [sg.Text('i-C4H10', size=(15, 1)), sg.InputText(key='i-C4H10',default_text='0')],
            [sg.Text('SF6', size=(15, 1)), sg.InputText(key='SF6',default_text='0')],
            [sg.Text('CO2', size=(15, 1)), sg.InputText(key='CO2',default_text='0')],
            [sg.Text('N2', size=(15, 1)), sg.InputText(key='N2',default_text='0')],
            [sg.Text('O2', size=(15, 1)), sg.InputText(key='O2',default_text='0')],
            [sg.Text('Ar', size=(15, 1)), sg.InputText(key='Ar',default_text='0')],
            [sg.Button('Insert mixture',font=('Times New Roman',12)),sg.Button('Back', font=('Times New Roman',12))]
            ]

    mixWin =sg.Window('New mixture',mixLayout)

    while True:
        event, values = mixWin.read()
        
        #Close program
        if event == "Back" or event == sg.WIN_CLOSED:
            break

        #Add new mixture to the db
        if event == "Insert mixture":
            for key in values:
                print(key, values[key])
                if key != "name" and float(values[key]) > 0:
                    sum = sum + float(values[key])

            #Check if sum of concentrations == 100
            if sum != 100: #sum of gases is not 100 -> error
                errorWindow("Gas mixture error","Sum of percentages is not 100")

            elif values["name"] == "":
                errorWindow("Gas mixture error","Mixture has no name")
            
            else: #add new mixture to db
                mixture = [values["name"],values["HFOze"],values["HFOyf"],values["R134a"],values["i-C4H10"],values["SF6"],values["CO2"],values["N2"],values["O2"],values["Ar"]] 
                sendMixture = ("INSERT INTO `mixtures` (name,HFOze,HFOyf,R134a,iC4H10,SF6,CO2,N2,O2,Ar) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                cursor.execute(sendMixture, mixture)
                db.commit()

            break

    mixWin.close()

#-----#

#Error message window
def errorWindow(errorName,errorMessage):
    errLayout=[
            [sg.Text(errorMessage,size=(50, 1), font=('Lucida',12,'bold'),justification='left')],
            [sg.Button('Ok',font=('Times New Roman',12))]
            ]

    errWin =sg.Window(errorName,errLayout)

    while True:
        event, values = errWin.read()
        
        #Close error window
        if event == "Ok" or event == sg.WIN_CLOSED:
            break

    errWin.close()

#-----#

#Get pid of process by its name
def get_pids_by_script_name(script_name):

    pids = []
    for proc in psutil.process_iter():

        try:
            cmdline = proc.cmdline()
            pid = proc.pid
        except psutil.NoSuchProcess:
            continue

        if (len(cmdline) >= 2
            and 'python' in cmdline[0]
            and os.path.basename(cmdline[1]) == script_name):

            pids.append(pid)

    return pids

#-----#

#main function for GUI
def main():
    #Connect to db to get mixture names
    mydb = mysql.connector.connect( 
            host="localhost",
            user="root",
            password="pcald32",
            database="labStrada"
        )

    mycursor = mydb.cursor()

    getColumns = ("SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='labStrada' AND `TABLE_NAME`='mixtures' ORDER BY ordinal_position")    
    mycursor.execute(getColumns)
    columns = mycursor.fetchall()

    getMixtures = ("SELECT * FROM mixtures")
    mycursor.execute(getMixtures)
    mixtures = mycursor.fetchall()
    
    totComposition = [] #list of: [mixname, gas1, gas2.....] for all mixtures in db

    for mixture in mixtures:
        mixComposition = [] #list of: [mixname, gas1, gas2.....] for a single mixture, updated for every cycle of the loop
        
        for i, element in enumerate(mixture):
            if element != 0:
                if columns[i][0] != 'name':
                    mixComposition.append(str(element)+"% "+columns[i][0])
                else:
                    mixComposition.append(str(element))
    
        totComposition.append(mixComposition[:])
        mixComposition = []

    #check status of running scripts
    hvMonit = True #If True the hv monitoring script is running
    gasKill = True #If True the gas kill script is running
    envMonit = True #If True the environmental monitoring script is running

    #if pid is = [] -> script is not running
    if get_pids_by_script_name('monitoring.py') == []:
        envMonit = False
    if get_pids_by_script_name('hvMonitor.py') == []:
        hvMonit = False
    if get_pids_by_script_name('gasKill.py') == []:
        gasKill = False

    #Change color of OK/NOT OK if script is running or not
    if hvMonit == True:
        hvColor = 'lime green'
        hvText = 'OK'
    elif hvMonit == False:
        hvColor = 'red'
        hvText = 'NOT OK'

    if gasKill == True:
        gasKillColor = 'lime green'
        gasKillText = 'OK'
    elif gasKill == False:
        gasKillColor = 'red'
        gasKillText = 'NOT OK'

    if envMonit == True:
        envMonitColor = 'lime green'
        envMonText = 'OK'
    elif envMonit == False:
        envMonitColor = 'red'
        envMonText = 'NOT OK'

    #Layout of main GUI panel
    layout=[
            [sg.Text('Script status',size=(20, 1), font=('Lucida',12,'bold'),justification='left')],
            [sg.Text('Envorinoment monitor',size=(20,1),font='Lucida',justification='left'),
            sg.Text(envMonText,size=(20,1),font=('Lucida',12,'bold'),text_color=envMonitColor,justification='left')],
            [sg.Text('HV monitor',size=(20,1),font='Lucida',justification='left'),
            sg.Text(hvText,size=(20,1),font=('Lucida',12,'bold'),text_color=hvColor,justification='left')],
            [sg.Text('Gas kill',size=(20,1),font='Lucida',justification='left'),
            sg.Text(gasKillText,size=(20,1),font=('Lucida',12,'bold'),text_color=gasKillColor,justification='left')],
            [sg.Text('Choose run type',size=(20, 1), font=('Lucida',12,'bold'),justification='left')],
            [sg.Combo(['Current scan','Efficiency scan','Noise scan', 'Stability scan', 'Resistivity measurement'],default_value='Current scan',key='scanType')],
            [sg.Text('Choose Mixture ',size=(30, 1), font=('Lucida',12,'bold'),justification='left')],
            [sg.Listbox(values=totComposition, select_mode='extended', key='mixture', size=(100, 6))],
            [sg.Text('Or enter new gas mixture',size=(30,1),font=('Lucida',12,'bold'),justification='left'),sg.Button('New mixture', font=('Times New Roman',12))],
            [sg.Button('Start scan', font=('Times New Roman',12)),sg.Button('Abort scan', font=('Times New Roman',12))]
            ]

    win =sg.Window('Start scan',layout)

    while True:
        event, values = win.read()
        
        #Close program
        if event == "Abort scan" or event == sg.WIN_CLOSED:
            break

        #Enter new mixture in db
        if event == "New mixture":
            newMixture(mydb,mycursor)

        #Start scan
        if event == "Start scan":
            if values['scanType'] == 'Current scan':
                print('You selected current scan')
                #print(values['mixture'][0][0])
                os.system("python3 /home/pcald32/labStrada/DAQ/currentScan/hvScan.py " + str(values['mixture'][0][0] + " currentScan"))

            elif values['scanType'] == 'Efficiency scan':
                print('You selected efficiency scan')
                os.system("python3 /home/pcald32/labStrada/DAQ/efficiencyScan/effScan.py " + str(values['mixture'][0][0] + " efficiencyScan"))

            elif values['scanType'] == 'Noise scan':
                print('You selected noise scan')
                os.system("python3 /home/pcald32/labStrada/DAQ/efficiencyScan/effScan.py " + str(values['mixture'][0][0] + " noiseScan"))

            elif values['scanType'] == 'Stability scan':
                print('You selected Stability scan')

            elif values['scanType'] == 'Resistivity measurement':
                print('You selected resistivity measurement')
                os.system("python3 /home/pcald32/labStrada/DAQ/currentScan/hvScan.py " + str(values['mixture'][0][0] + " argonScan"))
            
            break

    win.close()

if __name__ == '__main__':
    main()