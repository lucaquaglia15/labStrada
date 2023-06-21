import PySimpleGUI as sg
import mysql.connector #to connect to db to send the data
import psutil
import os
import shutil

def deleteScan(db,cursor,scanType):
    print("Opening delete scan panel")

    deleteScanLayout=[
            [sg.Text('Deleting run type '+scanType,size=(50, 1), font=('Lucida',12,'bold'),justification='left')],
            [sg.Text('Enter run number',size=(20, 1), font=('Lucida',12,'bold'),justification='left')],
            [sg.Text('Run number', size=(15, 1)), sg.InputText(key='runNum',default_text='')],
            [sg.Button('Delete run',font=('Times New Roman',12)),sg.Button('Back', font=('Times New Roman',12))]
            ]

    deleteScanWin =sg.Window('Delete run',deleteScanLayout)

    while True:
        event, values = deleteScanWin.read()

        if event == "Back" or event == sg.WIN_CLOSED:
            break

        elif event == 'Delete run' and values['runNum'] != "": #delete run
            #errorWindow("Confirm scan deletion","Are you sure you want to delete the scan?")
            
            #Delete locally
            if scanType == 'Current scan' or scanType == 'Resistivity scan': #current scan
                dir = '/home/pcald32/runs/currentScans/scan_'+values['runNum']
                dbTable = 'currentScan'
                try:
                    shutil.rmtree(dir)
                except Exception as err:
                    errorWindow("File not found","Run does not exist in local disk!")
            
            elif scanType == 'Efficiency scan' or scanType == 'Noise scan': #Efficiency or noise scan
                dir = '/home/pcald32/runs/efficiencyScans/scan_'+values['runNum']
                dbTable = 'efficiencyScan'
                try:
                    shutil.rmtree(dir)
                except Exception as err:
                    errorWindow("File not found","Run does not exist in local disk!")
            
            elif scanType == 'Stability scan': #Stability scan
                print('Stability scan not yet implemented')
                #dir = '/home/pcald32/runs/stabilityScan/scan_'+values['runNum']
                #dbTable = 'stabilityScan'
                #try:
                #    shutil.rmtree(dir)
                #except Exception as err:
                #    print("Run does not exist in local disk!")
                #    errorWindow("File not found","Run does not exist in local disk!")

            #Delete from db, after checking if run exists
            checkForRun = ("SELECT EXISTS(SELECT * FROM labStrada.%s WHERE runNumber=%s)") %(dbTable,values['runNum'])
            
            if  cursor.execute(checkForRun) == 1:
                deleteRun = ("DELETE FROM labStrada.%s WHERE runNumber = %s") %(dbTable,values['runNum'])
                cursor.execute(deleteRun)
                db.commit()
            
            else:
                errorWindow("File not found","Run does not exist in database!")

            break
            
        elif event == 'Delete run' and values['runNum'] == "": #number of run to be deleted not provided -> error
            errorWindow("Delete run error","Please entrer run number")
            break

    deleteScanWin.close()

#Fetch gas mixtures from db
def fetchGasMixtures(db,cursor):

    getColumns = ("SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='labStrada' AND `TABLE_NAME`='mixtures' ORDER BY ordinal_position")    
    cursor.execute(getColumns)
    columns = cursor.fetchall()

    getMixtures = ("SELECT * FROM mixtures")
    cursor.execute(getMixtures)
    mixtures = cursor.fetchall()
    
    totComposition = [] #list of: [mixname, gas1, gas2.....] for all mixtures in db

    for mixture in mixtures:
        mixComposition = [] #list of: [mixname, gas1, gas2.....] for a single mixture, updated for every cycle of the loop
        
        for i, element in enumerate(mixture):
            if element != 0:
                if columns[i][0] != 'name':
                    mixComposition.append(str(element)+"% "+columns[i][0])
                else:
                    mixComposition.append(str(element)+":")
    
        #totComposition.append(mixComposition[:])
        totComposition.append(' '.join(mixComposition[:]))
        mixComposition = []

    return totComposition

def deleteMixture(db,cursor,mixName):
    delete = ("DELETE FROM labStrada.mixtures WHERE name = (%s)")
    name = (mixName,)
    cursor.execute(delete,name)

#New mixture window
def newMixture(db,cursor):
    print("Opening new mixture panel")

    sum = 0 #sum of percentages, check of mixture sanity

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
                if key != "name" and float(values[key]) > 0:
                    sum = sum + float(values[key])

            #Check if mixture with same name but different conentrations exists
            checkForMixture = ("SELECT EXISTS(SELECT * FROM mixtures WHERE name=(%s))")
            name = (values["name"],)

            cursor.execute(checkForMixture,name)
            isMixture = cursor.fetchall()

            if isMixture[0][0] == 1: #mixture with this name already in db
                errorWindow("Gas mixture error","Mixture with same name but different concentration already exists in database")
            
            #Check if sum of concentrations == 100
            elif sum != 100: #sum of gases is not 100 -> error
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

    totComposition = fetchGasMixtures(mydb,mycursor)
    
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
            [sg.Combo(['Current scan','Efficiency scan','Noise scan', 'Stability scan', 'Resistivity measurement'],default_value='Current scan',font=('Lucida',12),key='scanType')],
            [sg.Text('Choose Mixture ',size=(30, 1), font=('Lucida',12,'bold'),justification='left')],
            [sg.Listbox(values=totComposition, select_mode='single', key='mixture', size=(100, 6),enable_events=True,font=('Lucida',12,'bold'))],
            [sg.Text('Enter new gas mixture',size=(30,1),font=('Lucida',12,'bold'),justification='left'),sg.Button('New mixture', font=('Times New Roman',12))],
            [sg.Text('Delete gas mixture',size=(30,1),font=('Lucida',12,'bold'),justification='left'),sg.Button('Delete mixture', font=('Times New Roman',12),disabled=True,key='deleteMixture')],
            [sg.Text('Delete run',size=(30,1),font=('Lucida',12,'bold'),justification='left'),sg.Button('Delete scan', font=('Times New Roman',12),key='deleteScan')],
            [sg.Button('Start scan', font=('Times New Roman',12)),sg.Button('Abort scan', font=('Times New Roman',12))]
            ]

    win =sg.Window('Start scan',layout)

    while True:
        event, values = win.read()

        #Close program
        if event == "Abort scan" or event == sg.WIN_CLOSED:
            break

        #If mixture is selected once from list and it is re-clicked
        #-> Remove selection and disable delete mixture button
        if event == 'mixture':
            metadata = win['mixture'].metadata
            selections = values['mixture']
            if metadata == selections:
                win['mixture'].update(set_to_index=[])
                win['mixture'].metadata = []
                values['mixture'] = []
                win['deleteMixture'].update(disabled=True)
            else:
                win['mixture'].metadata = values['mixture']

        #Enable delete mixture buttton if a gas mixture is selected from the list       
        if values['mixture'] != []:    
            win['deleteMixture'].update(disabled=False)
        
        #Enter new mixture in db
        if event == "New mixture":
            newMixture(mydb,mycursor)
            mydb.cmd_refresh(1)
            updatedMixtures = fetchGasMixtures(mydb,mycursor)
            win['mixture'].update(updatedMixtures)

        #Delete gas mixture new mixture in db
        if event == "deleteMixture":
            deleteMixture(mydb,mycursor,(values['mixture'][0]).split(':')[0])
            mydb.cmd_refresh(1)
            updatedMixtures = fetchGasMixtures(mydb,mycursor)
            win['mixture'].update(updatedMixtures)

        #Delete scan data both locally and from db
        if event == 'deleteScan':
            deleteScan(mydb,mycursor,values['scanType'])
        
        #Start scan
        if event == "Start scan":
            if values['scanType'] == 'Current scan': #General current scan
                print('You selected current scan')
                os.system("python3 /home/pcald32/labStrada/DAQ/currentScan/hvScan.py " + str(values['mixture'][0][0] + " currentScan"))

            elif values['scanType'] == 'Efficiency scan': #efficiency scan (muon trigger)
                print('You selected efficiency scan')
                os.system("python3 /home/pcald32/labStrada/DAQ/efficiencyScan/effScan.py " + str(values['mixture'][0][0] + " efficiencyScan"))

            elif values['scanType'] == 'Noise scan': #noise scan (random trigger)
                print('You selected noise scan')
                os.system("python3 /home/pcald32/labStrada/DAQ/efficiencyScan/effScan.py " + str(values['mixture'][0][0] + " noiseScan"))

            elif values['scanType'] == 'Stability scan': #stability scan
                print('You selected Stability scan')

            elif values['scanType'] == 'Resistivity measurement': #res scan
                print('You selected resistivity measurement')
                
                if str(values['mixture'][0][0]) != 'argon': #res scan but not Ar as the gas
                    errorWindow("Gas mixture error","You selected resistivity scan but not Ar as the gas")
                else: #res scan and Ar as the gas
                    os.system("python3 /home/pcald32/labStrada/DAQ/currentScan/hvScan.py " + str(values['mixture'][0][0] + " argonScan"))
            
            break

    win.close()

if __name__ == '__main__':
    main()