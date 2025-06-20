import time
from VME import VME
from scaler import scaler
import ROOT

def main():

    print("Connecting to VME bridge")
    VMEbridge = VME(1,0,0)
    handle = VMEbridge.connect()

    print("Initialzign scaler(s)")
    V830_1 = scaler(0x88880000)
    V830_2 = scaler(0x77770000)

    time.sleep(1)

    print("Resetting scaler(s)")
    V830_1.resetModule(VMEbridge,handle)
    V830_2.resetModule(VMEbridge,handle)

    time.sleep(1)

    print("Setting control register")
    V830_1.setControlRegister(VMEbridge,handle,0x0)
    V830_2.setControlRegister(VMEbridge,handle,0x0)

    time.sleep(1)

    print("Enabling channels")
    V830_1.enableChannels(VMEbridge,handle,0xFFFF)
    V830_1.enableChannels(VMEbridge,handle,0x00FF)

    time.sleep(1)

    print("Creating canvas and histogram")
    
    cScaler = ROOT.TCanvas()
    cScaler.cd()
    cScaler.Divide(1,2)

    cScaler.cd(1)
    hScaler1 = ROOT.TH1F("hScaler1","hScaler1",32,0.5,32.5)
    hScaler1.Draw("HISTO")

    cScaler.cd(2)
    hScaler2 = ROOT.TH1F("hScaler2","hScaler2",32,0.5,32.5)
    hScaler2.Draw("HISTO")

    counter=0

    while True:

        print("Reading scaler(s)")

        for i in range(32):
            data = V830_1.readCounters(VMEbridge,handle,(4*i) + 0x1000)
            #print(data," ",int(data,2))
            hScaler1.SetBinContent(i+1,int(data,2))
            cScaler.cd(1)
            hScaler1.Draw("HISTO")
        
        for i in range(16):
            data = V830_2.readCounters(VMEbridge,handle,(4*i) + 0x1000)
            #print(data," ",int(data,2))
            hScaler2.SetBinContent(i+1,int(data,2))
            cScaler.cd(2)
            hScaler2.Draw("HISTO")
            
        cScaler.Update()
        
        counter+=1
        
        if counter==30:
            break

        time.sleep(10)

    f = ROOT.TFile("/home/pcald32/runs/efficiencyScans/scan_477/scalers_test.root","RECREATE")
    f.cd()
    cScaler.Write("ScalerCounts")
    f.Close()

if __name__ == "__main__":
    main()