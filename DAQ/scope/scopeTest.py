import TeledyneLeCroyPy
import pandas as pd
import time

def get_trig_level(self, channel: int):
	#validate_channel_number(channel)
    print("test")
    return (self.query(f'C{channel}:TRIG_LEVEL?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=47

debug = True

def main():

    fOutData = open("waveTest.txt", mode="wt") #open file to write out waveforms

    scope = TeledyneLeCroyPy.LeCroyWaveRunner('VICP::90.147.203.158') #Connect to scoper via TCP/IP

    if debug:
        print(scope.idn) # Prints oscilloscope id

    scope.set_tdiv('20NS') #Set time base division of the scope
    #scope.set_vdiv(1,0.2) #amplitude in volts channel 1
    #scope.set_vdiv(2,0.2) #amplitude in volts channel 2
    #scope.set_vdiv(3,0.2) #amplitude in volts channel 3
    #scope.set_vdiv(4,0.2) #amplitude in volts channel 4
    scope.set_vdiv(1,2e-3) #amplitude in volts channel 1
    scope.set_vdiv(2,2e-3) #amplitude in volts channel 2
    scope.set_vdiv(3,2e-3) #amplitude in volts channel 3
    scope.set_vdiv(4,5e-1) #amplitude in volts channel 4
    #scope.set_trig_mode('AUTO')
    #0.055 = 55 mV
    #scope.set_voffset(1,0)
    scope.set_trig_source("C4")
    #print(get_trig_level(scope,1),scope.get_trig_source())
    #trgLevel = -100e-3
    #scope.set_trig_level("C1",trgLevel)
    #print(get_trig_level(scope,1))


    activeChannels = [1,2,3,4] #list of the channels which we want to record -> max is [1,2,3,4]

    trigNum = 10 #number of triggers we want to record

    start_time = time.time()

    for i in range(trigNum): #Loop on # of triggers
        
        #fOutData.write("trigger #" + str(i) + " channels:" + str(len(activeChannels)) + "\n") #Header in text file

        print('Waiting for trigger...') 

        scope.wait_for_single_trigger() # Halt the execution until there is a trigger
        
        #print('Trigger received: ',i+1) 
    
        data = {} #dictonary of dictionaries
        for n_channel in activeChannels:
            data[n_channel] = scope.get_waveform(n_channel=n_channel)

        wf = []

        for j,n_channel in enumerate(data): #Loop on dictionaries inside main dictionary (data)
            for i,_ in enumerate(data[n_channel]['waveforms']):                
                if j == 0: #first channel processed
                    df = pd.DataFrame(_)
                    df.columns = ['Time (s)','Amplitude ch ' + str(n_channel) + ' (V)']
                else:
                    df = pd.DataFrame(data[n_channel]['waveforms'][0]['Amplitude (V)'])
                    df.columns = ['Amplitude ch ' + str(n_channel) + ' (V)']
                
                #print(type(df))

                wf.append(df)
        
        wf = pd.concat(wf, axis=1)

        wf.to_csv(fOutData, sep='\t', index=False)
        print("--- %s seconds ---" % (time.time() - start_time))
        #fOutData.flush()

        #print('Data saved! Moving to next trigger') 
    
    #wf.to_csv(fOutData, sep='\t', index=False)
    fOutData.flush()
    
if __name__ == "__main__":
    main()