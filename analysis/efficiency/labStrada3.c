//
//  labStrada3.c
//  
//
//  Created by Sara Garetti on 21/05/23.
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
#include <unordered_set>

using namespace std;

void labStrada3(){

    TH1D *hTimeStrip[16];
    for (int i = 0; i < 16; i++) {
        hTimeStrip[i] =  new TH1D(("hTimeStrip_"+to_string(i)).c_str(),("hTimeStrip_"+to_string(i)).c_str(),100,0.,200.);
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
    //creo istogrammi per i 3 TDC
    TH1D *histoTime1 = new TH1D("histoTime1","time distribution TDC 1;Time;Counts",100,0.,190.);
    TH1D *histoTime2 = new TH1D("histoTime2","time distribution TDC 2;Time;Counts",100,0.,180.);
    TH1D *histoTime3 = new TH1D("histoTime3","time distribution TDC 3;Time;Counts",100,0.,210.);
    TH1D *histoProjectionX = new TH1D("histoProjectionX","histoProjectionX;Bin;Counts",8,0.,8.);
    TH1D *histoProjectionY = new TH1D("histoProjectionY","histoProjectionY;Bin;Counts",8,0.,8.);
    TH1D *histoClusterX = new TH1D("histoClusterX","istogramma delle cluster sulle strip X;Strip;Counts",8,1.,8.);
    TH1D *histoClusterY = new TH1D("histoClusterY","istogramma delle cluster sulle strip Y;Strip;Counts",8,1.,8.);
    /*char tito[80];
    char name[10];
    TH1F* arr[14];
    for (int i=0; i<6; i++) {
        sprintf(tito, "", );
        sprintf(name, "his%d", i);
        arr[i]=new TH1F(name,tito,250,-1, 1);
        arr[i]->histo;
        }*/
    //vado nella cartella in cui è contenuto lo scan di efficienza
    gSystem->cd("/home/pcald32/runs/efficiencyScans/");
    //numero del run
    int nrun;
    cout<<"Inserire il numero del run: ";
    cin>>nrun;
    gSystem->cd(("scan_"+to_string(nrun)).c_str());
    cout<<("scan_"+to_string(nrun)).c_str()<<endl;
    //int a+1=0;
    for(int a=0;a<1;a++){
        int countEv = 0;
        int countTrg = 0;
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
            
            /*order(channelX.begin(), channelX.end());
             order(channelY.begin(), channelY.end());*/

                if(channelX.size()!=0 && channelY.size()!=0){
                    countTrg = countTrg+1;
                    cout<<"\nHo registrato "<<countTrg<<"trigger\n"<<endl;
                    for(int y=0;y<channelY.size();y++){
                        for(int x=0;x<channelX.size();x++){
                            histo2D->Fill(channelX.at(x),channelY.at(y)-8);
                        }
                    }
                }
            
            /*if(channelX.size()!=0 && channelY.size()!=0){ //X AND Y
                countEv = countEv+1;
            }*/

            if(channelX.size()!=0){ //X ONLY
                countEv = countEv+1;
            }

            /*if(channelY.size()!=0){ //Y ONLY
                countEv = countEv+1;
            }*/

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
        
        
        double eff = (countEv/(double) 1000)*100;
        double errEff = TMath::Sqrt(eff*(100-eff)/1000);

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
        TCanvas *gTDC1 = new TCanvas("histoTempi TDC1");
        histoTime1->Draw();
        TCanvas *gTDC2 = new TCanvas("histoTempi TDC2");
        histoTime2->Draw();
        TCanvas *gTDC3 = new TCanvas("histoTempi TDC3");
        histoTime3->Draw();
        
        gSystem->cd("..");
        
    }
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
    
}
            
        

