//
//  analyzeEff.c
//  
//
//  Based on the code created by Sara Garetti on 21/05/23
//  Edited by Luca Quaglia and Daniela Rosso in 2024
//

#include <stdio.h>
#include <Riostream.h>
#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TMath.h"
#include <TCanvas.h>
#include "TNtuple.h"
#include "TH1F.h"
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
//#include<bit/stdc++.h>//to use return vector

using namespace std;
using namespace TMath;

bool lowLevelDebug = false;
bool middleLevelDebug = false;
bool highLevelDebug = true;

TF1 *fMuon_gammaX = new TF1("fMuon_gammaX","gaus(0)",0,300); //Gaussian + constant (value of the constant determined with the linear fit of the background)
TF1 *fMuon_gammaY = new TF1("fMuon_gammaY","gaus(0)",0,300); //Gaussian + constant (value of the constant determined with the linear fit of the background)

TF1 *muon_gamma_tempX = new TF1("muon_gamma_tempX","gaus(0)",0,300); //Gaussian + constant (value of the constant determined with the linear fit of the background)
TF1 *muon_gamma_tempY = new TF1("muon_gamma_tempY","gaus(0)",0,300); //Gaussian + constant (value of the constant determined with the linear fit of the background)

//Create TCanvas with desired cosmetics already applied
TCanvas *produceCanvas(bool logX, bool logY) {
	TCanvas *c = new TCanvas();
	c->SetFrameFillColor(0); //Transparent background
    c->SetFrameFillStyle(0);
    c->SetFrameBorderMode(0);
	c->SetGridx(); //Grid on x
	c->SetGridy(); //Grid on y 
	if (logX) c->SetLogx(); //Log on x, if needed
	if (logY) c->SetLogy(); //Log on y, if needed
	return c;
}

//Function to return the cluster size 
vector<double> clustering(vector<float> hits){
        vector <double> cluster;
        cluster.clear();
        sort(hits.begin(),hits.end());
        /*
        cout<<"Print ordered vector of hits"<<endl;
        for(int i=0;i< hits.size();i++){
        cout<<hits.at(i)<<endl;
        }*/

        for(int elem=0; elem<hits.size(); elem ++){
            int cont=1;
            for(int e=elem +1;e<hits.size();e++){
                if(hits.at(e) == ((hits.at(elem) +cont))){
                    cont ++;
                }
                else{
                    e=hits.size();
                }
            }
            elem= elem +cont -1;
            cluster.push_back(cont);
        }
        /*
        cout<<"Print cluster lengths"<<endl;
        for(int i=0;i< cluster.size();i++){
        cout<<cluster.at(i)<<endl;
        }*/
    return cluster;
}

//Find and return muon window
tuple <double,double,double> findMuonWindow(TH1F *timeProfile, TF1 *&muonGamma, int &r, float minMean, float maxMean, float minSTD, float maxSTD) {

	double muonStart, muonEnd, muonMean, avgGamma;

	//muonGamma->SetParLimits(0,0.,timeProfile->GetBinContent(timeProfile->GetMaximumBin())+0.1*(timeProfile->GetBinContent(timeProfile->GetMaximumBin())));
	//muonGamma->SetParLimits(1,140.,160.);
	//muonGamma->SetParLimits(2,1.,40.); 	
    muonGamma->SetParLimits(0,0.,timeProfile->GetBinContent(timeProfile->GetMaximumBin())+0.1*(timeProfile->GetBinContent(timeProfile->GetMaximumBin())));
	muonGamma->SetParLimits(1,minMean,maxMean);
	muonGamma->SetParLimits(2,minSTD,maxSTD); 	
	
    timeProfile->Fit(muonGamma,"RM"); //Fit with gaussian + constant
	string minuitstatus = string(gMinuit->fCstatu);
	cout << endl << endl << "Status: " << minuitstatus << endl << endl;
	if(minuitstatus.compare("CONVERGED ") != 0 && minuitstatus.compare("OK        ") != 0) r = -1;
	else r = 0;

	if (r == 0) { //Fit succesful, muon window = mean +- 3 sigma
		muonStart = muonGamma->GetParameter(1) - 3*muonGamma->GetParameter(2); 
		muonEnd = muonGamma->GetParameter(1) + 3*muonGamma->GetParameter(2);
		muonMean = muonGamma->GetParameter(1);
	}

	else {
		muonStart = 0; 
		muonEnd = 0;
		muonMean = 0;
	}

	return make_tuple(muonStart,muonEnd,muonMean);
}

//Create TH1F with desired cosmetics already applied
TH1F *produceTH1(string name, string title, string xAxisTitle, string yAxisTitle, int nBins, double xMin, double xMax) {
	TH1F *h = new TH1F(name.c_str(), title.c_str(), nBins, xMin, xMax);
	h->GetXaxis()->SetTitle(xAxisTitle.c_str());
	h->GetYaxis()->SetTitle(yAxisTitle.c_str());
	h->GetXaxis()->SetTitleFont(62);
	h->GetXaxis()->SetLabelFont(62);
	h->GetYaxis()->SetTitleFont(62);
	h->GetYaxis()->SetLabelFont(62);
	h->GetXaxis()->CenterTitle(true);
	h->GetYaxis()->CenterTitle(true);

	return h;
}

//-------------//
//  Main code  //
//-------------//

void analyzeEff(const int scan, const string detectorName){

    const int MAX_SIZE = 24; //maximum number of channels (3 TDCs, 8 channels each)

    bool isIn; //from input mapping (first column tells us if the strip is to be considered for analysis or not)
    int strip, TDCchannel;

    //Strip mapping
	ifstream mappingX, mappingY;
	mappingX.open("mappingX.txt");
	mappingY.open("mappingY.txt");
	
	int chX, strpX, muteX;
	int chY, strpY, muteY;
	vector <int> tdc_chX, rpc_strpX;//seconda e terza colonna mapping
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
	int finstripY = tdc_chY.back();

	map <int, int> strp_mapX;
	for (unsigned int i = 0; i < tdc_chX.size();i++) {
		strp_mapX.insert(pair<int, int>(tdc_chX.at(i),rpc_strpX.at(i)));
	}

	map <int, int> strp_mapY;//vettore di coppie unisce le due colonne di mapping
	for (unsigned int i = 0; i < tdc_chY.size();i++) {
		strp_mapY.insert(pair<int, int>(tdc_chY.at(i),rpc_strpY.at(i)));
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

    //Create .root output file 
    TFile *fOut = new TFile(("OutFile_ALICE_" + to_string(scan) + ".root").c_str(),"RECREATE");
    fOut->cd();
    TDirectory *cdtof[nfolders]; //Crate an array of folders that will be created inside the .root output file

    //Define histograms, one per HV point
    TH1F *time_profile_ALICEX[nfolders]; //Time profile - X plane
	TH1F *strp_profile_ALICEX[nfolders]; //Strip profile - X plane al hits
	TH1F *strp_profile_ALICE_muonsX[nfolders]; //Muon strip profile - X plane
	TH1F *muon_cluster_size_ALICEX[nfolders]; //Muon cluster size histo - X plane
	TH1F *muon_cluster_mult_ALICEX[nfolders]; //Muon cluster mult histo - X plane
	TH1F *time_profile_ALICEY[nfolders]; //Time profile - Y plane
	TH1F *strp_profile_ALICEY[nfolders]; //Strip profile - Y plane al hits
    TH1F *strp_profile_ALICE_muonsY[nfolders]; //Muon strip profile - Y plane
	TH1F *muon_cluster_size_ALICEY[nfolders]; //Muon cluster size histo - Y plane
	TH1F *muon_cluster_mult_ALICEY[nfolders]; //Muon cluster mult histo - Y plane
    //Temporary histos in case of fit failure
    TH1F *strp_profile_ALICE_tmpX; //Temporary strip profile histo if fit fails - X plane
	TH1F *time_profile_ALICE_tmpX; //Temporary time profile histo if fit fails - X plane
	TH1F *strp_profile_ALICE_tmpY; //Temporary strip profile histo if fit fails - Y plane
	TH1F *time_profile_ALICE_tmpY; //Temporary time profile histo if fit fails - Y plane

    //Useful variables
    bool hit_muonX = 0, hit_muonY = 0; //To check if there was a hit or not in a given trigger in X and Y planes
    int count_X = 0, count_Y = 0, count_XY = 0; //Muon counts on X, y and xy planes
    vector <float> muon_hitsX,muon_hitsY;
    vector <float> HVeff, HVapp,Imon;
    vector <float> eHVeff, eHVapp,eImon;
    vector <float> cluster_sizeX,cluster_sizeY;
    vector <float> e_cluster_sizeX, e_cluster_sizeY;
    vector <float> cluster_multX,cluster_multY;
    vector <float> e_cluster_multX, e_cluster_multY;
    vector <float> EffX,EffY,Eff2D;
    vector <float> e_EffX, e_EffY, e_Eff2D;

    for (int hv = 0; hv < nfolders; hv++) {

        string cartella = "HV" + to_string(hv+1); //Name for folder and histograms

        cdtof[hv]= fOut->mkdir(cartella.c_str()); //Create the folder in the .root output file

        //Canvas booking 
        TCanvas *c_time_profile_ALICEX = produceCanvas(false,false); //Time profile - X plane
        TCanvas *c_strp_profile_ALICEX = produceCanvas(false,false); //Strip profile of all hits - X plane
        TCanvas *c_strp_profile_ALICE_muonsX = produceCanvas(false,false); //Strip profile muons - X plane
        TCanvas *c_cluster_size_muon_ALICEX = produceCanvas(false,false); //Muon cluster size - X plane
        TCanvas *c_cluster_mult_muon_ALICEX = produceCanvas(false,false); //Muon cluster multiplicity - X plane
        TCanvas *c_time_profile_ALICEY = produceCanvas(false,false); //Time profile - Y plane
        TCanvas *c_strp_profile_ALICEY = produceCanvas(false,false); //Strip profile of all hits - Y plane
        TCanvas *c_strp_profile_ALICE_muonsY = produceCanvas(false,false); //Strip profile muons - Y plane
        TCanvas *c_cluster_size_muon_ALICEY = produceCanvas(false,false); //Muon cluster size - Y plane
        TCanvas *c_cluster_mult_muon_ALICEY = produceCanvas(false,false); //Muon cluster multiplicity - Y plane
        //TCanvas *c_time_profile_stripsX[16]; //Time profile for each strip - X plane
        //TCanvas *c_time_profile_stripsY[16]; //Time profile for each strip - Y plane
        //TCanvas *c_time_profile_ALICE_tmpX = produceCanvas(false,false); //Temporary time profile - x plane
        //TCanvas *c_time_profile_ALICE_tmpY = produceCanvas(false,false); //Temporary time profile - Y plane 

        //Create histograms
        time_profile_ALICEX[hv] = produceTH1("time_profile_X_"+cartella,"Time profile ALICE X " + cartella,"Time [ns]","Counts",200,-0.5,199.5);
		time_profile_ALICEY[hv] = produceTH1("time_profile_Y_"+cartella,"Time profile ALICE Y " + cartella,"Time [ns]","Counts",200,-0.5,199.5);
		strp_profile_ALICEX[hv] = produceTH1("strip_profile_all_hits_X"+cartella,"Strip profile ALICE X all hits " + cartella,"Strip","Counts",8,0.5,8.5);
		strp_profile_ALICEY[hv] = produceTH1("strip_profile_all_hits_Y"+cartella,"Strip profile ALICE Y all hits " + cartella,"Strip","Counts",8,0.5,8.5);
		strp_profile_ALICE_muonsX[hv] = produceTH1("strip_profile_muons_X"+cartella,"Strip profile ALICE X muons " + cartella,"Strip","Muon counts",8,0.5,8.5);
		strp_profile_ALICE_muonsY[hv] = produceTH1("strip_profile_muons_Y"+cartella,"Strip profile ALICE Y muons " + cartella,"Strip","Muon counts",8,0.5,8.5);
		muon_cluster_size_ALICEX[hv] = produceTH1("muon_cluster_size_X"+cartella,"Muon cluster size ALICE X " + cartella,"Muon cluster size [strips]","Counts",8,0,8);
		muon_cluster_size_ALICEY[hv] = produceTH1("muon_cluster_size_Y"+cartella,"Muon cluster size ALICE Y " + cartella,"Muon cluster size [strips]","Counts",8,0,8);
		muon_cluster_mult_ALICEX[hv] = produceTH1("muon_cluster_mult_X"+cartella,"Muon cluster multiplicity ALICE X " + cartella,"Muon cluster multiplicity","Counts",8,0,8);
		muon_cluster_mult_ALICEY[hv] = produceTH1("muon_cluster_mult_Y"+cartella,"Muon cluster multiplicity ALICE Y " + cartella,"Muon cluster multiplicity","Counts",8,0,8);
		time_profile_ALICE_tmpX = produceTH1("time_profile_X_temp_"+cartella,"Time profile ALICE X (temporary) " + cartella,"Time [ns]","Counts",200,-0.5,199.5);
		time_profile_ALICE_tmpY = produceTH1("time_profile_Y_temp_"+cartella,"Time profile ALICE Y (temporary) " + cartella,"Time [ns]","Counts",200,-0.5,199.5);
		strp_profile_ALICE_tmpX = produceTH1("strip_profile_all_hits_X_temp"+cartella,"Strip profile ALICE X all hits (temporary) " + cartella,"Strip","Counts",8,0.5,8.5);
		strp_profile_ALICE_tmpY = produceTH1("strip_profile_all_hits_Y_temp"+cartella,"Strip profile ALICE Y all hits (temporary) " + cartella,"Strip","Counts",8,0.5,8.5);

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
        //Get HV and current data
        fHV->cd();
        TH1F *hHVapp = (TH1F*)fHV->Get((detectorName + "_HV_app_"+to_string(hv+1)).c_str());
        TH1F *hHVeff = (TH1F*)fHV->Get((detectorName + "_HV_eff_"+to_string(hv+1)).c_str());
        TH1F *hHVmon = (TH1F*)fHV->Get((detectorName + "_HV_mon_"+to_string(hv+1)).c_str());
        TH1F *hImon = (TH1F*)fHV->Get((detectorName + "_I_mon_"+to_string(hv+1)).c_str());
        HVeff.push_back(hHVeff->GetMean());
        HVapp.push_back(hHVapp->GetMean());
        eHVeff.push_back(hHVeff->GetMeanError());
        eHVapp.push_back(hHVapp->GetMeanError());
        Imon.push_back(hImon->GetMean());
        eImon.push_back(hImon->GetMeanError());


        //------------------//
        //  Open DIP file   //
        //------------------//
        fDIP->cd();

        //------------------//
        //  Open DAQ file   //
        //------------------//
        fDAQ->cd();

        //Get number of triggers
        TParameter<float>* nTrg = (TParameter<float>*)fDAQ->Get("numTriggers");
        float numTrg = nTrg->GetVal();

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
                
                if (channel[i] >= instripX && channel[i] <= finstripX) {
                    strp_profile_ALICEX[hv]->Fill(strp_mapX.lower_bound(channel[i])->second); //Strip profile of all hits in muon spill
					time_profile_ALICEX[hv]->Fill(time[i]);//Time profile of the chamber in the muon spill
                }

                else if (channel[i] >= instripY && channel[i] <= finstripY) {
                    //if (channel[i] != 9) {
                    strp_profile_ALICEY[hv]->Fill(strp_mapY.lower_bound(channel[i])->second); //Strip profile of all hits in muon spill
                    time_profile_ALICEY[hv]->Fill(time[i]);//Time profile of the chamber in the muon spill
                    //} 
                }
            }

            cout << endl;
            
        } //End of loop on TTree entries

        tuple<double,double,double> muonWindowX;
		tuple<double,double,double> muonWindowY;
        int fitStatusX = 0, fitStatusY = 0;

		muonWindowX = findMuonWindow(time_profile_ALICEX[hv],fMuon_gammaX,fitStatusX,140.,160.,1.,40.);
        if (scan == 413 && hv != 7) {
            muonWindowY = findMuonWindow(time_profile_ALICEY[hv],fMuon_gammaY,fitStatusY,150.,180.,1.,40.);
        }
        else if (scan == 413 && hv == 7) {
            muonWindowY = findMuonWindow(time_profile_ALICEY[hv],fMuon_gammaY,fitStatusY,120.,160.,1.,40.);
        }

        float startMuonX = get<0>(muonWindowX);
		float endMuonX = get<1>(muonWindowX);
		float meanX = get<2>(muonWindowX);

        float startMuonY = get<0>(muonWindowY);
		float endMuonY = get<1>(muonWindowY);
		float meanY = get<2>(muonWindowY);

        //Re-process data after time profile fit -> Only hits in the muon window
        for (int entry = 0; entry < treeDAQ->GetEntries(); entry++) { 
			muon_hitsX.clear();
			muon_hitsY.clear();

            treeDAQ->GetEntry(entry);
            
            int channel[MAX_SIZE];
            float time[MAX_SIZE];
            
            treeDAQ->SetBranchAddress("channels",channel);
            treeDAQ->SetBranchAddress("times",time);

            for (int i = 0; i < size; i++) {//size per ogni elemento quantoo lunghi i vettori
				//Muon hits profile
                if ((channel[i] >= instripX && channel[i] <= finstripX) && (time[i] <= endMuonX && time[i] >= startMuonX))  { //muon on X
                    strp_profile_ALICE_muonsX[hv]->Fill(strp_mapX.lower_bound(channel[i])->second); //Strip profile of muons
                    hit_muonX = 1; //The X plane saw something, set the counter to true, it wil be reset at the end of the event
                    muon_hitsX.push_back(strp_mapX.lower_bound(channel[i])->second);
                }

                else if ((channel[i] >= instripY && channel[i] <= finstripY) && (time[i] <= endMuonY && time[i] >= startMuonY)) { //muon on Y
                    strp_profile_ALICE_muonsY[hv]->Fill(strp_mapY.lower_bound(channel[i])->second); //Strip profile of muons
                    hit_muonY = 1; //The X plane saw something, set the counter to true, it wil be reset at the end of the event
                    muon_hitsY.push_back(strp_mapY.lower_bound(channel[i])->second);
                }

            }

            //Muon clustering
            //On X - only if we have muon hits
            if(muon_hitsX.size()!=0){
                vector <double> clusterX;
                clusterX=clustering(muon_hitsX);
                muon_cluster_size_ALICEX[hv]->FillN(clusterX.size(),clusterX.data(),nullptr);//tutti pesano 1
                muon_cluster_mult_ALICEX[hv]->Fill(clusterX.size());
            }

            //On Y - only if we have muon hits
            if(muon_hitsY.size()!=0){
                vector <double> clusterY;
                clusterY=clustering(muon_hitsY);
                muon_cluster_size_ALICEY[hv]->FillN(clusterY.size(),clusterY.data(),nullptr);//tutti pesano 1
                muon_cluster_mult_ALICEY[hv]->Fill(clusterY.size());
            }

            //Efficiency calculation counters
            if (hit_muonX == 1) count_X++; //Increase the number of events where at least one muon was seen by the RPC - X plane
			if (hit_muonY == 1) count_Y++; //Increase the number of events where at least one muon was seen by the RPC - Y plane
			if (hit_muonX == 1 && hit_muonY == 1) count_XY++; //Increase the number of events where at least one muon was seen by the RPC - X and Y plane

            hit_muonX = 0; //reset the bool for muon events counting - X plane
			hit_muonY = 0; //reset the bool for muon events counting - Y plane
        } //End of loop on tree entries

        //Vectors for muon cluster size vs HV
        cluster_sizeX.push_back(muon_cluster_size_ALICEX[hv]->GetMean());
        cluster_multX.push_back(muon_cluster_mult_ALICEX[hv]->GetMean());
        cluster_sizeY.push_back(muon_cluster_size_ALICEY[hv]->GetMean());
        cluster_multY.push_back(muon_cluster_mult_ALICEY[hv]->GetMean());
        e_cluster_sizeX.push_back(muon_cluster_size_ALICEX[hv]->GetMeanError());
        e_cluster_sizeY.push_back(muon_cluster_size_ALICEY[hv]->GetMeanError());
        e_cluster_multX.push_back(muon_cluster_mult_ALICEX[hv]->GetMeanError());
        e_cluster_multY.push_back(muon_cluster_mult_ALICEY[hv]->GetMeanError());

        //Vectors for muon efficiency vs HV
		double raweffX = (count_X/(double)numTrg); //Raw efficiency - X plane
		double raweffY = (count_Y/(double)numTrg); //Raw efficiency - Y plane
		double raweff2D = (count_XY/(double)numTrg); //Raw efficiency - 2D
        double raw_e_effX = TMath::Sqrt(raweffX*(1-raweffX)/numTrg);// Efficiency error - X plane
        double raw_e_effY = TMath::Sqrt(raweffY*(1-raweffY)/numTrg);//Efficiency error -Y plane
        double raw_e_eff2D = TMath::Sqrt(raweff2D*(1-raweff2D)/numTrg);//Efficiency error - 2D

        EffX.push_back(raweffX);
        EffY.push_back(raweffY);
        Eff2D.push_back(raweff2D);
        e_EffX.push_back(raw_e_effX);
        e_EffY.push_back(raw_e_effY);
        e_Eff2D.push_back(raw_e_eff2D);

        //Reset efficiency counters 
        count_X = 0;
        count_Y = 0;
        count_XY = 0;

        if (highLevelDebug) {
            cout << "HV point " << hv+1 << " rawEffX " << raweffX << endl;
            cout << "HV point " << hv+1 << " rawEffY " << raweffY << endl;
            cout << "HV point " << hv+1 << " rawEff2D " << raweff2D << endl;
        }
        
        //Draw histograms per HV value (i.e. time profile, strip profile, muon cluster size, muon cluster mult)
        //X-plane
        c_time_profile_ALICEX->cd(); //Time profile - X plane
	    time_profile_ALICEX[hv]->Draw("HISTO");
        fMuon_gammaX->Draw("SAME"); //Draw fit function on same canvas
        
        c_strp_profile_ALICEX->cd(); //Strip profile of all hits - X plane
        strp_profile_ALICEX[hv]->Draw("HISTO");

        c_strp_profile_ALICE_muonsX->cd(); //Strip profile muons - X plane
        strp_profile_ALICE_muonsX[hv]->Draw("HISTO");

        c_cluster_size_muon_ALICEX->cd(); //Muon cluster size - X plane
        muon_cluster_size_ALICEX[hv]->Draw("HISTO");

        c_cluster_mult_muon_ALICEX->cd(); //Muon cluster multiplicity - X plane
        muon_cluster_mult_ALICEX[hv]->Draw("HISTO");
        
        c_cluster_size_muon_ALICEY->cd(); //Muon cluster size - Y plane
        muon_cluster_size_ALICEY[hv]->Draw("HISTO");
        
        c_cluster_mult_muon_ALICEY->cd(); //Muon cluster multiplicity - Y plane
        muon_cluster_mult_ALICEY[hv]->Draw("HISTO");
        
        //Y-plane
        c_time_profile_ALICEY->cd(); //Time profile - Y plane
        time_profile_ALICEY[hv]->Draw("HISTO");
        fMuon_gammaY->Draw("SAME"); //Draw fit function on same canvas
        
        c_strp_profile_ALICEY->cd(); //Strip profile of all hits - Y plane
        strp_profile_ALICEY[hv]->Draw("HISTO");

        c_strp_profile_ALICE_muonsY->cd(); //Strip profile muons - Y plane
        strp_profile_ALICE_muonsY[hv]->Draw("HISTO");
        
        c_cluster_size_muon_ALICEY->cd(); //Muon cluster size - Y plane
        muon_cluster_size_ALICEY[hv]->Draw("HISTO");
        
        c_cluster_mult_muon_ALICEY->cd(); //Muon cluster multiplicity - Y plane
        muon_cluster_mult_ALICEY[hv]->Draw("HISTO");

        //Save the canvases in the .root output file
        fOut->cd();
        cdtof[hv]->cd();
        c_time_profile_ALICEX->Write(("Time_profile_ALICE_X_" + cartella).c_str());
        c_strp_profile_ALICEX->Write(("Strip_profile_ALICE_X_" + cartella).c_str());
        c_strp_profile_ALICE_muonsX->Write(("Strip_muons_profile_ALICE_X_" + cartella).c_str());
        c_cluster_size_muon_ALICEX->Write(("Cluster_size_muon_ALICE_X_" + cartella).c_str());
        c_cluster_mult_muon_ALICEX->Write(("Cluster_mult_muon_ALICE_X_" + cartella).c_str());

        c_time_profile_ALICEY->Write(("Time_profile_ALICE_Y_" + cartella).c_str());
        c_strp_profile_ALICEY->Write(("Strip_profile_ALICE_Y_" + cartella).c_str());
        c_strp_profile_ALICE_muonsY->Write(("Strip_muons_profile_ALICE_Y_" + cartella).c_str());
        c_cluster_size_muon_ALICEY->Write(("Cluster_size_muon_ALICE_Y_" + cartella).c_str());
        c_cluster_size_muon_ALICEY->Write(("Cluster_mult_muon_ALICE_Y_" + cartella).c_str());

        //End of the loop, delete all objects and rename strings for different .root objects inputs
        HVfile = "scan_" + to_string(scan) +"_CAEN_";
        DIPfile = "scan_" + to_string(scan) +"_DIP_";
        DAQfile = "scan_" + to_string(scan) +"_DAQ_";

    } //End of loop on HV points

    //Plots of quantities vs HV - outside of the loop on HV values
    TCanvas *efficiency_HV = produceCanvas(false,false);
    efficiency_HV->cd();
    TGraph *gEff2D= new TGraphErrors(HVeff.size(), &HVeff[0], &Eff2D[0],&eHVeff[0],&e_Eff2D[0]);
    gEff2D->SetTitle("Efficienza(HV) di X e Y; HV; efficienza");
    gEff2D->SetMarkerStyle(8);
    gEff2D->SetMarkerSize(2);
    gEff2D->GetYaxis()->SetRangeUser(0,1);
    gEff2D->Draw("AP");

    TCanvas *efficiency_X = produceCanvas(false,false);
    efficiency_X->cd();
    TGraph *gEffX= new TGraphErrors(HVeff.size(), &HVeff[0], &EffX[0],&eHVeff[0],&e_EffX[0]);
    gEffX->SetTitle("Efficienza(HV) di X; HV; efficienza");
    gEffX->SetMarkerStyle(8);
    gEffX->SetMarkerSize(2);
    gEffX->GetYaxis()->SetRangeUser(0,1);
    gEffX->Draw("AP");

    TCanvas *efficiency_Y = produceCanvas(false,false);
    efficiency_Y->cd();
    TGraph *gEffY= new TGraphErrors(HVeff.size(), &HVeff[0], &EffY[0],&eHVeff[0],&e_EffY[0]);
    gEffY->SetTitle("Efficienza(HV) di Y; HV; efficienza");
    gEffY->SetMarkerStyle(8);
    gEffY->SetMarkerSize(2);
    gEffY->GetYaxis()->SetRangeUser(0,1);
    gEffY->Draw("AP");

    TCanvas *c_cluster_sizeX = produceCanvas(false,false);
    c_cluster_sizeX->cd();
    TGraph *g_cluster_sizeX = new TGraphErrors(HVeff.size(),&HVeff[0],&cluster_sizeX[0],&eHVeff[0],&e_cluster_sizeX[0]);
    g_cluster_sizeX->SetTitle("Cluster size X (HV);HV;cluster_size");
    g_cluster_sizeX->SetMarkerStyle(8);
    g_cluster_sizeX->SetMarkerSize(2);
    g_cluster_sizeX->Draw("AP");

    TCanvas *c_cluster_sizeY = produceCanvas(false,false);
    c_cluster_sizeY->cd();
    TGraph *g_cluster_sizeY = new TGraphErrors(HVeff.size(),&HVeff[0],&cluster_sizeY[0],&eHVeff[0],&e_cluster_sizeY[0]);
    g_cluster_sizeY->SetTitle("Cluster size Y (HV); HV; cluster_size");
    g_cluster_sizeY->SetMarkerStyle(8);
    g_cluster_sizeY->SetMarkerSize(2);
    g_cluster_sizeY->Draw("AP");

    TCanvas *c_iv=produceCanvas(false,false);
    c_iv->cd();
    TGraph *iv= new TGraphErrors(HVeff.size(),&HVeff[0],&Imon[0],&eHVeff[0], &eImon[0]);
    iv->SetTitle("I(HV); HV; I");
    iv->SetMarkerStyle(8);
    iv->SetMarkerSize(2);
    iv->Draw("AP");

    //Save canveses in the .root output file
    fOut->cd();
    efficiency_HV->Write(("Grafico_eff_XY_"+ to_string(scan)).c_str());
    c_cluster_sizeX->Write(("Cluster_size_X_HV_"+ to_string(scan)).c_str());
    c_cluster_sizeY->Write(("Cluster_size_Y_HV"+ to_string(scan)).c_str());
    efficiency_X->Write(("Grafico_eff_X_" + to_string(scan)).c_str());
    efficiency_Y->Write(("Grafico_eff_Y_" + to_string(scan)).c_str());
}