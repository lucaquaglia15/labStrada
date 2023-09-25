#include <stdio.h>
#include <Riostream.h>
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TMath.h"
#include <TH1D.h>
#include <TH2D.h>
#include <TCanvas.h>
#include "TNtuple.h"
#include "TGraphErrors.h"
#include "TStyle.h"
#include <vector>
#include "TSystem.h"
#include "TSystemDirectory.h"
#include "TBrowser.h"
#include <fstream>
#include <bits/stdc++.h>  

using namespace std;

void analyzeWaveForm() {

    ifstream hdati("/home/pcald32/labStrada/DAQ/scope/waveTest.txt");

    double time, amplitude;
    vector<double> vTime;
    vector<double> vAmplitude[4];
    //vector<vector<double>> vAmplitude;

    bool firstLine = false;
    int nChannels = 0;

    string line, delimiter = "\t", temp;

    while (getline(hdati,line)) { //Read input file
       size_t pos = 0;
       if (line.find("trigger") != std::string::npos) { //line contains "trigger #i-th"
        nChannels = stoi(line.substr(line.find(":") + 1)); //Get number of channels in each trigger 
        //New trigger -> clear vectors
        vTime.clear();
        for (int kk = 0; kk < 4; kk++) {
            cout << vAmplitude[kk].size() << "\t";
            cout << endl;
            vAmplitude[kk].clear();
        }
        //Skip line
        continue;
       }

       else {
        int iter = 0; //to keep track of iterations in while
        while ((pos = line.find(delimiter)) != std::string::npos) {
            temp = line.substr(0, pos); //Fine delimitere "\t" in order to separate the data for each sample
            line.erase(0, pos + delimiter.length());
            
            if (iter == 0) { //push back to time vector
                vTime.push_back(stod(temp)*1e+9);
            }
            else { //push back to i-th channel amplitude
                if (!isnan(stof(temp))) {
                    vAmplitude[iter-1].push_back(stod(temp)*1e+3);
                }
            }
            iter++;
        }
       }
    
    }

    TGraph *gTest = new TGraph(vAmplitude[0].size(),&vTime[0],&vAmplitude[0][0]);
    gTest->GetXaxis()->SetTitle("Time [ns]");
    gTest->GetYaxis()->SetTitle("Amplitude [mV]");
    gTest->SetMarkerStyle(8);
    gTest->SetMarkerSize(1);
    gTest->SetMarkerColor(kRed);
    
    TCanvas *cTest = new TCanvas();
    gTest->Draw("APL");
}