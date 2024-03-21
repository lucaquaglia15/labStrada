import TeledyneLeCroyPy
import pandas as pd

debug = False

def main():

    f = open("waveTest.txt", mode="wt") #open file to write out waveforms

    scope = TeledyneLeCroyPy.LeCroyWaveRunner('VICP::90.147.203.158') #Connect to scoper via TCP/IP

    if debug:
        print(scope.idn) # Prints oscilloscope id

    scope.set_tdiv('20NS') #Set time base division of the scope
    scope.set_vdiv(1,0.002) #amplitude in volts channel 1
    scope.set_vdiv(2,0.2) #amplitude in volts channel 2
    scope.set_vdiv(3,0.2) #amplitude in volts channel 3
    #scope.set_trig_mode('AUTO')
    #0.055 = 55 mV
    scope.set_trig_level("C1",0.005)

    activeChannels = [1] #list of the channels which we want to record -> max is [1,2,3,4]

    trigNum = 2 #number of triggers we want to record

    for i in range(trigNum): #Loop on # of triggers
        
        f.write("trigger #" + str(i) + " channels:" + str(len(activeChannels)) + "\n") #Header in text file

        print('Waiting for trigger...') 

        scope.wait_for_single_trigger() # Halt the execution until there is a trigger

        data = {} #To store data from multiple channels

        globalOut = []
        temp = []

        for n_channel in activeChannels:
            data[n_channel] = scope.get_waveform(n_channel=n_channel)

        for j in range(len(data[1]['waveforms'][0]['Time (s)'])):
            for n_channel in activeChannels:
                if n_channel == 1: #Append time only once, no matter the number of channels (time scale is common to all channels)
                    temp.append(data[n_channel]['waveforms'][0]['Time (s)'][j])
                    temp.append(data[n_channel]['waveforms'][0]['Amplitude (V)'][j])
                else:
                    temp.append(data[n_channel]['waveforms'][0]['Amplitude (V)'][j])
            
            globalOut.append(temp) #append the i-th sample to the gloabl output vector, which is organized in this way:
            temp = [] #Clear the i-th sample
            
            #trigger #1
            #Time sample 1  \t  Ch1 sample 1  \t  Ch2 sample 1  \t  Ch3 sample 1  \t  Ch4 sample 1  \n
            #....           \t  ....          \t  ....          \t  ....          \t  ....          \n 
            #....           \t  ....          \t  ....          \t  ....          \t  ....          \n 
            #Time sample n  \t  Ch1 sample 1  \t  Ch2 sample 1  \t  Ch3 sample 1  \t  Ch4 sample 1  \n
            #Trigger #2
            #Time sample 1  \t  Ch1 sample 1  \t  Ch2 sample 1  \t  Ch3 sample 1  \t  Ch4 sample 1  \n
            #....           \t  ....          \t  ....          \t  ....          \t  ....          \n 
            #....           \t  ....          \t  ....          \t  ....          \t  ....          \n 
            #Time sample n  \t  Ch1 sample 1  \t  Ch2 sample 1  \t  Ch3 sample 1  \t  Ch4 sample 1  \n
            #.....
            #Trigger n


        if debug:
            print(len(globalOut))
            for x in globalOut:
                print(x)

        for j in range(len(globalOut)):
            for k in (globalOut[j]):
                f.write(str(k) + "\t")
            f.write("\n")

        #data is a dictionary of dictionaries
        #-> waveforms is the key to acces the full waveform, which is itself a dictionary
        #-> waveforms is like this [{'Time (s)': t, f'Amplitude (V)': s} for t,s in zip(times,samples)]
        #it is a list of dictionaries, with a single element -> accessed by [0] and then ['Time (s)'] is the key to access time
        #print(type(data['waveforms'][0]['Time (s)']))
        #print(len(data['waveforms'][0]['Time (s)']))

    f.flush() #Write out to the txt file


if __name__ == "__main__":
    main()