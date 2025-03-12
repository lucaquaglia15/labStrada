import pandas as pd
import time
import matplotlib.pyplot as plt

def main():

    fIn = '/home/pcald32/labStrada/DAQ/scope/waveTest.txt'

    waveData = pd.read_csv(fIn, sep='\t', header=None)
    waveData.columns = ["Time (s)","Amplitude ch 1 (V)","Amplitude ch 2 (V)","Amplitude ch 3 (V)","Amplitude ch 4 (V)"]
    print(waveData)
    
    time = waveData["Time (s)"].tolist()
    ch1 = waveData["Amplitude ch 1 (V)"].tolist()
    ch2 = waveData["Amplitude ch 2 (V)"].tolist()
    ch3 = waveData["Amplitude ch 3 (V)"].tolist()
    ch4 = waveData["Amplitude ch 4 (V)"].tolist()

    print(len(time))
    print(len(ch1))
    print(len(ch2))
    print(len(ch3))
    print(len(ch4))

    time = [float(val)*1e9 for i, val in enumerate(time) if i % 2003 != 0]
    ch1 = [float(val)*1e3 for i, val in enumerate(ch1) if i % 2003 != 0]
    ch2 = [float(val)*1e3 for i, val in enumerate(ch2) if i % 2003 != 0]
    ch3 = [float(val)*1e3 for i, val in enumerate(ch3) if i % 2003 != 0]
    ch4 = [float(val)*1e3 for i, val in enumerate(ch4) if i % 2003 != 0]

    print(len(time))
    print(len(ch1))
    print(len(ch2))
    print(len(ch3))
    print(len(ch4))

    generalTime = time[:2002]
    eventsCh1 = [ch1[i:i+2002] for i in range (0,len(ch1),2002)]
    eventsCh2 = [ch2[i:i+2002] for i in range (0,len(ch2),2002)]
    eventsCh3 = [ch3[i:i+2002] for i in range (0,len(ch3),2002)]
    eventsCh4 = [ch4[i:i+2002] for i in range (0,len(ch4),2002)]
    
    print(len(generalTime))
    print(len(eventsCh1))
    print(len(eventsCh2))
    print(len(eventsCh3))
    print(len(eventsCh4))

    #[time[i] for i in range(len(time)) if (i + 1) % n != 0]

    
    figTest, axTest = plt.subplots(figsize=(10, 10))
    axTest.plot(generalTime, eventsCh1[0], marker='o', linestyle='-', color = 'r', label='CH1')
    axTest.plot(generalTime, eventsCh4[0], marker='o', linestyle='-', color = 'g', label='CH4')

    #Format the x-axis to show time and rotate labels
    #axTest.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    #plt.xticks(rotation=45)

    #Cosmetics
    plt.xlabel('Time [ns]')
    plt.ylabel('Amplitude [mV]')
    plt.title('Test waeform')
    plt.legend()
    plt.grid()
   
    plt.show()

   


if __name__ == "__main__":
    main()