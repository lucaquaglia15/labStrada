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
#include <unordered_set>
#include "fstream"

using namespace std;
using namespace TMath;

//Funzioni per fittare il time profile dei vari TDC
TF1 *fitGausTDC1 = new TF1("fitGausTDC1","gaus(0)",0.,200.);
TF1 *fitGausTDC2 = new TF1("fitGausTDC2","gaus(0)",0.,160.);
TF1 *fitGausTDC3 = new TF1("fitGausTDC3","gaus(0)",0.,200.);

//os.system("root -l -q .x 'current.C(221)'")

void noise(const string mapping){

    //Open strip mapping
    ifstream hMap(mapping.c_str());

    int s = 0, c = 0;

    while (hMap >> s >> c) {
        cout << s << "\t" << c << endl;
    }

    /*int chX, strpX, muteX;
	int chY, strpY, muteY;
	vector <int> tdc_chX, rpc_strpX;
	vector <int> tdc_chY, rpc_strpY;

	while (mappingX >> muteX >> chX >> strpX) {

		if (muteX == 1) {
			tdc_chX.push_back(chX);
			rpc_strpX.push_back(strpX);
		}

		else continue;
	}

	while (mappingY >> muteY >> chY >> strpY) {

		if (muteY == 1) {
			tdc_chY.push_back(chY);
			rpc_strpY.push_back(strpY);
		}

		else continue;
	}

	int instripX = tdc_chX.front();
	int instripY = tdc_chY.front();
	int finstripX = tdc_chX.back();
	int finstripY = tdc_chY.back();*/

    int numTrigger = 100000; //number of random triggers
    float triggerDuration = 770; //ns

    bool debug = false;

    TH1D *hTimeStrip[24];
    for (int i = 0; i < 24; i++) {
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
    //creo istogrammi per i 3 TDC
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
    int nrun;
    cout<<"Inserire il numero del run: ";
    cin>>nrun;
    gSystem->cd(("scan_"+to_string(nrun)).c_str());
    cout<<("scan_"+to_string(nrun)).c_str()<<endl;
    //int a+1=0;
    for(int a=0;a<1;a++){
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

        float hitTime[24]; //Time of the hits per strip

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
            
            if (debug)
            cout << "Evento " << i << " size " << size << endl;
            
            for(int k=0;k<size;k++){
                
                //cout << channel[k] << "\t" << time[k] << endl;
                hTimeStrip[channel[k]]->Fill(time[k]); //Fill time histogram per strip

                if (channel[k] == 4) {
                    cout << time[k] << " ns" << endl;
                    //hitTime[channel[k]] += time[k];
                }

                hitTime[channel[k]] += time[k];

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
                    if (debug)
                        cout<<"\nLe strip x sono:"<<channel[l] << endl;
                    histoProjectionX->Fill(channel[l]);
                    stripsX.clear();
                }else if(channel[l]>7){
                    vector <double> stripsY(8,channel[l]);
                    channelY.push_back(channel[l]);
                    timeY.push_back(time[l]);
                    if (debug)
                        cout<<"Le strip y sono:"<<channel[l]<< endl;
                    histoProjectionY->Fill(channel[l]-8);
                    stripsY.clear();
                }
            }
            
            /*order(channelX.begin(), channelX.end());
             order(channelY.begin(), channelY.end());*/

                if(channelX.size()!=0 && channelY.size()!=0){
                    countTrg = countTrg+1;
                    if (debug)
                        cout<<"\nHo registrato "<<countTrg<<"trigger\n"<<endl;
                    for(int y=0;y<channelY.size();y++){
                        for(int x=0;x<channelX.size();x++){
                            histo2D->Fill(channelX.at(x),channelY.at(y)-8);
                        }
                    }
                }
            
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
            
            if (debug)
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
        
        
        double eff = (countEv/(double) 1500)*100;
        double errEff = TMath::Sqrt(eff*(100-eff)/1500);
 
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

        cout << histoProjectionX->GetBinContent(1) << endl;
        //cout << "Rate strip 0: " << histoProjectionX->GetBinContent(1)/((numTrigger*triggerDuration - hitTime[0])*1e-9*(2.5*50)) << " Hz/cm^2" << endl;
        
        for (int j = 0; j < 24; j++) {
            if (j >= 0 && j <= 7) {
                cout << hitTime[j] << endl;
                cout << "Rate strip " << to_string(j) << ": " << histoProjectionX->GetBinContent(j+1)/((numTrigger*triggerDuration - hitTime[j])*1e-9*(2.1*50)) << " Hz/cm^2" << endl;
            }
            else if (j >= 8 && j <= 15) {
                cout << hitTime[j] << endl;
                cout << "Rate strip " << to_string(j-8) << ": " << histoProjectionY->GetBinContent(j-8+1)/((numTrigger*triggerDuration - hitTime[j])*1e-9*(2.1*50)) << " Hz/cm^2" << endl;
            }
        }

        TCanvas *gTDC1 = new TCanvas("histoTempi TDC1");
        histoTime1->Draw();        
        TCanvas *gTDC2 = new TCanvas("histoTempi TDC2");
        histoTime2->Draw();
        TCanvas *gTDC3 = new TCanvas("histoTempi TDC3");
        histoTime3->Draw();

        gSystem->cd("..");

        

        
    } //fine ciclo for sui punti di HV

    for(int j=0;j<hveff.size();j++){
        cout<<hveff.at(j)<<endl;
    }
 
    TCanvas *ghistoClusterX = new TCanvas("histoClusterX");
    histoClusterX->Draw();
    TCanvas *ghistoClusterY = new TCanvas("histoClusterY");
    histoClusterY->Draw();

    TCanvas *cTimeTDC1 = new TCanvas();
    TCanvas *cTimeTDC2 = new TCanvas();
    TCanvas *cTimeTDC3 = new TCanvas();

    cTimeTDC1->cd();
    cTimeTDC1->Divide(2,4);
    cTimeTDC2->cd();
    cTimeTDC2->Divide(2,4);
    cTimeTDC3->cd();
    cTimeTDC3->Divide(2,4);

    for (int i = 0; i < 8; i++) {
        cTimeTDC1->cd(i+1);
        hTimeStrip[i]->Draw("HISTO");
    }

    for (int i = 0; i < 8; i++) {
        cTimeTDC2->cd(i+1);
        hTimeStrip[i+8]->Draw("HISTO");
    }

    for (int i = 0; i < 8; i++) {
        cTimeTDC2->cd(i+1);
        hTimeStrip[i+16]->Draw("HISTO");
    }  

    /*for (int i = 0; i < 24; i++) {

    }*/
}    