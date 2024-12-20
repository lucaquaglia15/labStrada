//
//  labStrada3.c
//  
//
//  Created by Sara Garetti on 21/05/23
//  Edited by Luca Quaglia in 2024
//

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
#include "TH1F.h"
#include "TH3.h"
#include "TH2.h"
#include "TMath.h"
#include "TGraphErrors.h"
#include "TStyle.h"
#include <vector>
#include "TSystem.h"
#include "TSystemDirectory.h"
#include "TBrowser.h"
#include "TOrdCollection.h"
#include "TList.h"
#include <TString.h>
#include <algorithm>
#include "TParameter.h"
#include <unordered_set>
#include <filesystem> //to count the number of folders in each scan

using namespace std;
using namespace TMath;

//Funzioni per fittare il time profile dei vari TDC
//TF1 *fitGausTDC1 = new TF1("fitGausTDC1","gaus(0)",0.,200.);
//TF1 *fitGausTDC2 = new TF1("fitGausTDC2","gaus(0)",0.,200.);
//TF1 *fitGausTDC3 = new TF1("fitGausTDC3","gaus(0)",0.,200.);

bool lowLevelDebug = false;
bool middleLevelDebug = false;
bool highLevelDebug = false;

void labStrada3(const int scan, const string detectorName){

    const int MAX_SIZE = 24; //maximum number of channels (3 TDCs, 8 channels each)

    //Open mappping files
    ifstream hMappingX("mappingXnew.txt");
    ifstream hMappingY("mappingYnew.txt");

    bool isIn; //from input mapping (first column tells us if the strip is to be considered for analysis or not)
    int strip, TDCchannel;

    //Mapping of TDC channel <-> strip
    int channelsX[MAX_SIZE], channelsY[MAX_SIZE];
    int stripsX[MAX_SIZE], stripsY[MAX_SIZE];
    int counterX = 0, counterY = 0;

    while (hMappingX >> isIn >> strip >> TDCchannel) {
        if (isIn) {
            stripsX[counterX] = strip;
            channelsX[counterX] = TDCchannel;
            counterX++;
        }
    } 

    while (hMappingY >> isIn >> strip >> TDCchannel) {
        if (isIn) {
            stripsY[counterY] = strip;
            channelsY[counterY] = TDCchannel;
            counterY++;
        }
    }

    int size = 0; //variable used due to how DAQ code is written
    //size is the number of fired strips in each trigger and it's
    //needed while reading data from the DAQ TTree

    int numTrigger = 0; //variable used to keep track of the number of triggers for each HV point 
    //also saved in the DAQ tree

    //Global path of where the files of an efficiency scan are saved
    string folder = "/home/pcald32/runs/efficiencyScans/scan_"+to_string(scan)+"/";
    string HVfile = "scan_" + to_string(scan) +"_CAEN_";
    string DIPfile = "scan_" + to_string(scan) +"_DIP_";
    string DAQfile = "scan_" + to_string(scan) +"_DAQ_";
    
    gSystem->cd(folder.c_str());
    
    //Count number of folders (one folder per HV value)
    int nfolders = 0; //number of folders in the scan = number of hv points
    for (auto const& dir_entry :std::filesystem::directory_iterator{folder}) {
    	nfolders++;
    }

    //Loop on all folders
    //for (int hv = 0; hv < nfolders; hv++) {
    TH1F *hTimeTDC1 = new TH1F("hTimeTDC1","hTimeTDC1",200,-0.5,199.5);
    TH1F *hTimeTDC2 = new TH1F("hTimeTDC2","hTimeTDC2",200,-0.5,199.5);
    TH1F *hTimeTDC3 = new TH1F("hTimeTDC3","hTimeTDC3",200,-0.5,199.5);

    TH1F *hHitTDC1 = new TH1F("hHitTDC1","hHitTDC1",24,-0.5,23.5);
    TH1F *hHitTDC2 = new TH1F("hHitTDC2","hHitTDC2",24,-0.5,23.5);
    TH1F *hHitTDC3 = new TH1F("hHitTDC3","hHitTDC3",24,-0.5,23.5);

    for (int hv = 0; hv < nfolders; hv++) {

        //Add suffix to files, according to the folder
        HVfile += "HV" + to_string(hv+1) + ".root";
        DIPfile += "HV" + to_string(hv+1) + ".root";
        DAQfile += "HV" + to_string(hv+1) + ".root";

        if (lowLevelDebug) { //print names of input files
            cout << HVfile << endl;
            cout << DIPfile << endl;
            cout << DAQfile << endl;
        }
        
        TFile *fHV = new TFile((folder + "HV_" + to_string(hv+1) + "/" + HVfile).c_str(),"READ");
        TFile *fDIP = new TFile((folder + "HV_" + to_string(hv+1) + "/" + DIPfile).c_str(),"READ");
        TFile *fDAQ = new TFile((folder + "HV_" + to_string(hv+1) + "/" + DAQfile).c_str(),"READ");

        //----------------//
        //  Open HV file  //
        //----------------//
        fHV->cd();

        //------------------//
        //  Open DIP file   //
        //------------------//
        fDIP->cd();

        //------------------//
        //  Open DAQ file   //
        //------------------//
        fDAQ->cd();
        TTree *treeDAQ = (TTree*)fDAQ->Get("treeDAQ");
        treeDAQ->SetBranchAddress("size", &size);

        for (int entry = 0; entry < treeDAQ->GetEntries(); entry++) {
            treeDAQ->GetEntry(entry);

            int channel[MAX_SIZE];
            float time[MAX_SIZE];
            
            treeDAQ->SetBranchAddress("channels",channel);
            treeDAQ->SetBranchAddress("times",time);

            for (int i = 0; i < size; i++) {
                cout << time[i] << "\t" << channel[i] << "\n";
                
                if (channel[i] >= 0 && channel[i] <= 7) {
                    hTimeTDC1->Fill(time[i]);
                    hHitTDC1->Fill(channel[i]);
                }

                else if (channel[i] >= 8 && channel[i] <= 15) {
                    hTimeTDC2->Fill(time[i]);
                    hHitTDC2->Fill(channel[i]);
                }

                if (channel[i] >= 16 && channel[i] <= 23) {
                    hTimeTDC3->Fill(time[i]);
                    hHitTDC3->Fill(channel[i]);
                }
            }

            cout << endl;
            
        } //End of loop on TTree entries

        //End of the loop, delete all objects and rename strings for different .root objects inputs
        HVfile = "scan_" + to_string(scan) +"_CAEN_";
        DIPfile = "scan_" + to_string(scan) +"_DIP_";
        DAQfile = "scan_" + to_string(scan) +"_DAQ_";

    } //End of loop on HV points

    new TCanvas();
    hTimeTDC1->Draw("HISTO");
    new TCanvas();
    hHitTDC1->Draw("HISTO");
    new TCanvas();
    hTimeTDC2->Draw("HISTO");
    new TCanvas();
    hHitTDC2->Draw("HISTO");
    new TCanvas();
    hTimeTDC3->Draw("HISTO");
    new TCanvas();
    hHitTDC3->Draw("HISTO");

}

/*
    TH1D *hTimeStrip[16];
    //for (int i = 0; i < 16; i++) {
    //    hTimeStrip[i] =  new TH1D(("hTimeStrip_"+to_string(i)).c_str(),("hTimeStrip_"+to_string(i)).c_str(),100,0.,200.);
    //}

    for (int i = 0; i < 16; i++) {
        hTimeStrip[i] =  new TH1D(("hTimeStrip_"+to_string(i)).c_str(),("hTimeStrip_"+to_string(i)).c_str(),770,0.,770.);
    }

    vector <Int_t> channel[24];
    vector <Float_t> time[24];
    vector <double> channelX;
    vector <float> timeX;
    vector <double> channelY;
    vector <float> timeY;
    vector <double> strips={0,1,2,3,4,5,6,7};
    vector <double> efficency, errEfficiency;
    vector <double> hveff;
    vector <int> clustersX;
    vector <int> clustersY;
    vector <int> channelXord;
    //creo un istogramma 2D
    TH2I *histo2D = new TH2I("histo2D","X OR Y",8,0,8,8,0,8);
    TH2I *histo2Dcut = new TH2I("histo2Dcut","X OR Y cut",8,0,8,8,0,8);
    //creo istogrammi per i 3 TDC
    //TH1D *histoTime1 = new TH1D("histoTime1","time distribution TDC 1;Time;Counts",100,0.,190.);
    //TH1D *histoTime2 = new TH1D("histoTime2","time distribution TDC 2;Time;Counts",100,0.,180.);
    //TH1D *histoTime3 = new TH1D("histoTime3","time distribution TDC 3;Time;Counts",100,0.,210.);
    TH1D *histoTime1 = new TH1D("histoTime1","time distribution TDC 1;Time;Counts",770,0.,770.);
    TH1D *histoTime2 = new TH1D("histoTime2","time distribution TDC 2;Time;Counts",770,0.,770.);
    TH1D *histoTime3 = new TH1D("histoTime3","time distribution TDC 3;Time;Counts",770,0.,770.);
    TH1D *histoProjectionX = new TH1D("histoProjectionX","histoProjectionX;Bin;Counts",8,0.,8.);
    TH1D *histoProjectionY = new TH1D("histoProjectionY","histoProjectionY;Bin;Counts",8,0.,8.);
    TH1D *histoClusterX = new TH1D("histoClusterX","istogramma delle cluster sulle strip X;Strip;Counts",8,1.,8.);
    TH1D *histoClusterY = new TH1D("histoClusterY","istogramma delle cluster sulle strip Y;Strip;Counts",8,1.,8.);
    TH1D *histoMuonX = new TH1D("histoMuonX","histoMuonX",8,0.,8.);
    TH1D *histoMuonY = new TH1D("histoMuonY","histoMuonY",8,0.,8.);


    //vado nella cartella in cui è contenuto lo scan di efficienza
    gSystem->cd("/home/pcald32/runs/efficiencyScans/");
    //numero del run
    //int nrun;
    //cout<<"Inserire il numero del run: ";
    //cin>>nrun;
    
    gSystem->cd(("scan_"+to_string(nrun)).c_str());
    cout<<("scan_"+to_string(nrun)).c_str()<<endl;
    //int a+1=0;
    for(int a=0;a<10;a++){
        int countEv = 0;
        int countTrg = 0;
        int xCounter = 0, yCounter = 0, xyCounter = 0;
        //int countEv = 0;
        //a+1=a+1+1;
        gSystem->cd(("HV_"+to_string(a+1)).c_str());
        cout<<"Sto aprendo la cartella: "<<("HV_"+to_string(a+1)).c_str()<<endl;
        string caen = "_CAEN_";
        string daq = "_DAQ_";
        string dip = "_DIP_";
        TFile *scanCAEN = new TFile (("scan_"+to_string(nrun)+caen+"HV"+to_string(a+1)+".root").c_str(),"READ");
        TFile *scanDAQ = new TFile (("scan_"+to_string(nrun)+daq+"HV"+to_string(a+1)+".root").c_str(),"READ");
        //cout<<"Sto leggendo il file CAEN: "<<("scan_"+to_string(nrun)+caen+"HV"+to_string(a+1)+".root").c_str()<<endl;
        //cout<<"Sto leggendo il file DAQ: "<<("scan_"+to_string(nrun)+daq+"HV"+to_string(a+1)+".root").c_str()<<endl;
        //leggo tree e branches
        TTree *tree = (TTree*)scanDAQ->Get("treeDAQ");
        TH1F *HVeff = (TH1F*)scanCAEN->Get(("ECOgas_HV_eff_"+to_string(a+1)).c_str());
        hveff.push_back(HVeff->GetMean());

        //loop sugli ingressi del tree
        for(int i=0;i<tree->GetEntries();i++){
            int size = 0;
            //countEv=countEv+1;
            tree->SetBranchAddress("size",&size);
            tree->GetEvent(i);
            int channel[24]={0};
            float time[24]={0};
            int chXnew[30]={0};
            int chYnew[30]={0};
            int channelMinY[8]={0};
            tree->SetBranchAddress("channels",&channel[0]);
            tree->SetBranchAddress("times",&time[0]);
            tree->GetEvent(i);
            cout << "Evento " << i << " size " << size << endl;
            for(int k=0;k<size;k++){

                hTimeStrip[channel[k]]->Fill(time[k]); //Fill time histogram per strip

                if(channel[k]<=7){
                    histoTime1->Fill(time[k]);
                }
                else if(channel[k]>7&&channel[k]<=15){
                    histoTime2->Fill(time[k]);
                }
                else if(channel[k]>15){
                    histoTime3->Fill(time[k]);
                }
            }

            for(int l=0;l<size;l++){
                if(channel[l]<=7){
                    vector <double> stripsX(8,channel[l]);
                    channelX.push_back(channel[l]);
                    timeX.push_back(time[l]);
                    cout<<"\nLe strip x sono:"<<channel[l] << endl;
                    histoProjectionX->Fill(channel[l]);
                    stripsX.clear();
                }else if(channel[l]>7){
                    vector <double> stripsY(8,channel[l]);
                    channelY.push_back(channel[l]);
                    timeY.push_back(time[l]);
                    cout<<"Le strip y sono:"<<channel[l]<< endl;
                    histoProjectionY->Fill(channel[l]-8);
                    stripsY.clear();
                }
            }
        

                if(channelX.size()!=0 && channelY.size()!=0){
                    countTrg = countTrg+1;
                    cout<<"\nHo registrato "<<countTrg<<"trigger\n"<<endl;
                    for(int y=0;y<channelY.size();y++){
                        for(int x=0;x<channelX.size();x++){
                            histo2D->Fill(channelX.at(x),channelY.at(y)-8);
                        }
                    }
                }
            
            if(channelX.size()!=0 && channelY.size()!=0){ //X AND Y
                countEv = countEv+1;
            }

            //if(channelX.size()!=0){ //X ONLY
            //    countEv = countEv+1;
            }

            //if(channelY.size()!=0){ //Y ONLY
            //    countEv = countEv+1;
            //}

            int cluster = 1;
            for(int j=1; j<channelX.size();j++){
                    if(channelX.at(j)==channelX.at(j-1)+1){
                        cluster++;
                    }
                    else{
                        clustersX.push_back(cluster);
                        cluster=1;
                    }
            }
            clustersX.push_back(cluster);
            cluster=1;
            
            cout<<"Evento "<<i<<" "<<"Cluster size delle x: "<<clustersX.at(i)<<endl;
            
            for(int j=1; j<channelY.size();j++){
                    if(channelY.at(j)==channelY.at(j-1)+1){
                        cluster++;
                    }
                    else{
                        clustersY.push_back(cluster);
                        cluster=1;
                    }
            }
            clustersY.push_back(cluster);
            
            channelX.clear();
            channelY.clear();
            timeX.clear();
            timeY.clear();
        }
        
        for(int j=0; j<clustersX.size(); j++){
            histoClusterX->Fill(clustersX.at(j));
        }
        
        for(int j=0; j<clustersY.size(); j++){
            histoClusterY->Fill(clustersY.at(j));
        }
        
        
        double eff = (countEv/(double) 150)*100;
        double errEff = TMath::Sqrt(eff*(100-eff)/150);

        efficency.push_back(eff);
        errEfficiency.push_back(errEff);
        //cout<<"\nHo registrato "<<countEv<<"eventi totali\n"<<endl;
        cout<<"Efficienza calcolata: "<<eff<<endl;
        cout<<"\nHo registrato "<<countTrg<<"trigger\n"<<endl;
        
        TCanvas *ghPY = new TCanvas("histo proiezione Y");
        histoProjectionY->Draw();
        TCanvas *ghPX = new TCanvas("histo proiezione X");
        histoProjectionX->Draw();
        
        //histo2D->DrawCopy("colz");
        TCanvas *gh = new TCanvas("X OR Y");
        gStyle->SetPalette(55);
        gStyle->SetOptStat(1111);
        histo2D->GetXaxis()->SetTitle("StripX");
        histo2D->GetYaxis()->SetTitle("StripY");
        histo2D->Draw("COLZ");

        int maxCountsTDC1 = histoTime1->GetMaximum();
        int maxCountsTDC2 = histoTime2->GetMaximum();
        int maxCountsTDC3 = histoTime3->GetMaximum();
        
        double meanTDC1 = histoTime1->GetXaxis()->GetBinCenter(histoTime1->GetMaximumBin());
        double meanTDC2 = histoTime2->GetXaxis()->GetBinCenter(histoTime2->GetMaximumBin());
        double meanTDC3 = histoTime3->GetXaxis()->GetBinCenter(histoTime3->GetMaximumBin());

        fitGausTDC1->SetParLimits(0,maxCountsTDC1-0.1*maxCountsTDC1,maxCountsTDC1+0.1*maxCountsTDC1);
        fitGausTDC2->SetParLimits(0,maxCountsTDC2-0.1*maxCountsTDC2,maxCountsTDC2+0.1*maxCountsTDC2);
        fitGausTDC3->SetParLimits(0,maxCountsTDC3-0.1*maxCountsTDC3,maxCountsTDC3+0.1*maxCountsTDC3);
        
        fitGausTDC1->SetParLimits(1,meanTDC1-0.1*meanTDC1,meanTDC1+0.1*meanTDC1);
        //fitGausTDC2->SetParLimits(1,meanTDC2-0.1*meanTDC2,meanTDC2+0.05*meanTDC2);
        fitGausTDC2->SetParameter(1,meanTDC2);
        fitGausTDC3->SetParLimits(1,meanTDC3-0.1*meanTDC3,meanTDC3+0.1*meanTDC3);
       
        fitGausTDC1->SetParLimits(2,0,10);
        fitGausTDC2->SetParLimits(2,0,5);
        fitGausTDC3->SetParLimits(2,0,10);
        
        TCanvas *gTDC1 = new TCanvas("histoTempi TDC1");
        histoTime1->Fit("fitGausTDC1", "M+");
        histoTime1->Draw();
        double minMuon1 = fitGausTDC1->GetParameter(1) - 3*fitGausTDC1->GetParameter(2);
        double maxMuon1 = fitGausTDC1->GetParameter(1) + 3*fitGausTDC1->GetParameter(2);
        
        TCanvas *gTDC2 = new TCanvas("histoTempi TDC2");
        histoTime2->GetXaxis()->SetRangeUser(120,160);
        histoTime2->Fit("fitGausTDC2", "M+");
        histoTime2->GetXaxis()->SetRangeUser(0,200);
        histoTime2->Draw();

        double minMuon2 = fitGausTDC2->GetParameter(1) - 3*fitGausTDC2->GetParameter(2);
        //double maxMuon2 = fitGausTDC2->GetParameter(1) + 3*fitGausTDC2->GetParameter(2);
        double maxMuon2 = 160;

        cout << "Min muon1 " << minMuon1 << " max muon 1 " << maxMuon1 << endl;
        cout << "Min muon2 " << minMuon2 << " max muon 2 " << maxMuon2 << endl;

        TCanvas *gTDC3 = new TCanvas("histoTempi TDC3");
        histoTime3->Draw();

        vector<int> channelXcut, channelYcut;

        for(int i=0;i<tree->GetEntries();i++){
            int size = 0;
            //countEv=countEv+1;
            tree->SetBranchAddress("size",&size);
            tree->GetEvent(i);
            int channel[24]={0};
            float time[24]={0};
            int chXnew[30]={0};
            int chYnew[30]={0};
            int channelMinY[8]={0};
            tree->SetBranchAddress("channels",&channel[0]);
            tree->SetBranchAddress("times",&time[0]);
            tree->GetEvent(i);
            cout << "Evento " << i << " size " << size << endl;
            bool x = false, y = false; //true se c'è hit sulle x o y
            for(int k=0;k<size;k++){
                if (channel[k] >= 0 && channel[k] <= 7) { //TDC1
                    if (time[k] >= minMuon1 && time[k] <= maxMuon1) { //siamo nella muon window del TDC1
                        x = true;
                        histoMuonX->Fill(channel[k]);
                        channelXcut.push_back(channel[k]);
                    }
                }

                else if (channel[k] >= 8 && channel[k] <= 15) { //TDC2
                    if (time[k] >= minMuon2 && time[k] <= maxMuon2) { //siamo nella muon window del TDC2
                        y = true;
                        histoMuonY->Fill(channel[k]-8);
                        channelYcut.push_back(channel[k]-8);
                    }
                }
                
            }

            if(channelXcut.size()!=0 && channelYcut.size()!=0){
                for(int y=0;y<channelYcut.size();y++){
                    for(int x=0;x<channelXcut.size();x++){
                        histo2Dcut->Fill(channelXcut.at(x),channelYcut.at(y));
                    }
                }
            }
            channelXcut.clear();
            channelYcut.clear();

            if (x == true) {
                xCounter++;
            }

            if (y == true) {
                yCounter++;
            }

            if (x == true && y == true) {
                xyCounter++;
            }
            
            channelX.clear();
            channelY.clear();
            timeX.clear();
            timeY.clear();
        }
        
        gSystem->cd("..");
        
        cout << "x counter " << xCounter << " y counter " << yCounter << " x and y counter " << xyCounter << endl;

        

    } //fine ciclo for sui punti di HV

    for(int i=0;i<efficency.size();i++){
        cout<<efficency.at(i)<<endl;
    }
    for(int j=0;j<hveff.size();j++){
        cout<<hveff.at(j)<<endl;
    }
    TGraphErrors *gr1 = new TGraphErrors(hveff.size(),&hveff[0],&efficency[0],NULL,&errEfficiency[0]);
    gr1->SetMarkerStyle(20);
    gr1->SetMarkerColor(2);
    gr1->SetMarkerSize(1);
    gr1->SetName("effScan");
    gr1->SetTitle ("Efficiency Scan");
    gr1->GetYaxis()->SetTitle("Efficiency");
    gr1->GetXaxis()->SetTitle("HV (V)");
    //new TCanvas();
    gr1->Draw("AP");
    TCanvas *ghistoClusterX = new TCanvas("histoClusterX");
    histoClusterX->Draw();
    TCanvas *ghistoClusterY = new TCanvas("histoClusterY");
    histoClusterY->Draw();

    TCanvas *cTimeTDC1 = new TCanvas();
    TCanvas *cTimeTDC2 = new TCanvas();

    cTimeTDC1->cd();
    cTimeTDC1->Divide(2,4);
    cTimeTDC2->cd();
    cTimeTDC2->Divide(2,4);

    for (int i = 0; i < 8; i++) {
        cTimeTDC1->cd(i+1);
        hTimeStrip[i]->Draw("HISTO");
    }

    for (int i = 0; i < 8; i++) {
        cTimeTDC2->cd(i+1);
        hTimeStrip[i+8]->Draw("HISTO");
    }

    TCanvas *c1 = new TCanvas();
        c1->cd();
        histoMuonX->Draw("HISTO");
    TCanvas *c2 = new TCanvas();
        c2->cd();
        histoMuonY->Draw("HISTO");

    TCanvas *c2dCuts = new TCanvas();
        c2dCuts->cd();
        histo2Dcut->Draw("COLZ");
    
}    */