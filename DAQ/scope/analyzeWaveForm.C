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
#include <ifstream>

void analyzeWaveForm() {

    ifstream hdati();
    hdati.open("/home/pcald32/labStrada/DAQ/scope/readme.txt");

    double time, amplitude;
    vector<double> vTime, vAmplitude;

    bool drawn = false;

    while (hdati >> time >> amplitude) {
        
    }

    TGraph *gTest = new TGraph(vTime.size();&vTime[0],&vAmplitude[0]);
    gTest->GetXaxis()->SetTitle("Time [ns]");
    gTest->GetYaxis()->SetTitle("Amplitude [mV]");
    gTest->SetMarkerStyle(8);
    gTest->SetMarkerSize(1);
    gTest->Draw("APL");


}