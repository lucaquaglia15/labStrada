//Root & C++ classes
#include "TTree.h"
#include "TBranch.h"
#include "TSystem.h"

#include "TH1F.h"
#include "TH2F.h"
#include "TF1.h"
#include "Riostream.h"
#include "TGraphErrors.h"
#include "TCanvas.h"
#include "TPaveText.h"
#include "TStyle.h"
#include "TMath.h"
#include <fstream>
#include <TStyle.h>
#include "TString.h"
#include "TFile.h"

#include "TAxis.h"
#include <iostream>
#include <vector>
#include <stdlib.h> 
#include <string>
#include <iterator>
#include <numeric>
#include <map>
#include "Fit/FitResult.h"
#include "TMarker.h"
#include "TLine.h"
#include <array>
#include <tuple>


//---------------------------//
//                   		 //
//    Get I and HV values    //
//                           //
//---------------------------//

//vector <double> hvReader(string scanFolder, int scan, int file_count, bool verbose) {
tuple<float,float,float,float,float,float> hvReader(string scanFolder, int scan, int point) {

	double hvEff, eHVeff, iMon, eImon, hvMon, eHVmon;

	gSystem->cd(scanFolder.c_str());

    TFile *f = new TFile(("scan_" + to_string(scan) + "_CAEN_HV" + to_string(point) + ".root").c_str(),"READ");
    TH1F *HVeff = (TH1F*)f->Get(("ALICE-2-2_HV_app_"+to_string(point)).c_str());
    TH1F *HVmon = (TH1F*)f->Get(("ALICE-2-2_HV_mon_"+to_string(point)).c_str());
    TH1F *Imon = (TH1F*)f->Get(("ALICE-2-2_I_mon_"+to_string(point)).c_str());
    
    hvEff = (HVeff->GetMean());
    eHVeff = (HVeff->GetMeanError());
    iMon = (Imon->GetMean());
    eImon = (Imon->GetMeanError());
    hvMon = (HVmon->GetMean());
    eHVmon = (HVmon->GetMeanError());
		
    f->Close();

	return make_tuple(hvEff, eHVeff, iMon, eImon, hvMon, eHVmon);
}

using namespace std;

const string txtExt = ".txt"; //txt extension
const string rootExt = "CAEN.root"; //root extension
const string folder = "/home/pcald32/runs/digitizer/scan_"; //folder with data
const string detectorName = "ALICE-2-2"; //RPC name in CAEN.root files
const int file_count = 8;
const float sampFreq = 1.; //1 Gs/s sampling frequancy of the digitizer
const int sampNumber = 1024; //number of samples per trigger fixed to 1024 by design
float amplitude = 1000.; //1 V peak to peak
float convFactor = amplitude/(float)4096; //Conv factor between samples and mV
int numberOfSigmas = 5;

//1 Gs/s -> sample number = ns
const int muonMin = 130, muonMax = 250;
const int noiseMin = 30, noiseMax = 100; 

TF1* fit_eff;

bool verbose = false; //true = prints debug, false = no printout
bool verbose2 = false;

//void analyzeDigitizer(const int run, const int file_count) {
void analyzeDigitizer(const int run, const int hvpoints) {

	cout << "\n\nStarting digitizer data analysis!\n\n" << endl;

	cout << "Run number: " << run << endl;

	//Enter the scan folder
	string scanFolder = folder + to_string(run) + "/";
	gSystem->cd(scanFolder.c_str());

    remove(("outFile_ALICE_"+to_string(run)+".root").c_str());

    //Compute time vector for each event
    float time = 0;
    vector<float> times;
    for (int i = 0; i < sampNumber; i++) {
        if (i == 0) times.push_back(0);
        else {
            time = time + (sampNumber/sampFreq)/sampNumber;
            times.push_back(time);
        }
    }

    tuple<double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double> analysisResults;
    tuple<float, float, float, float, float, float> caenParam;
    vector<double> eff, eEff,muCS,eMuCS,muCM,eMuCM,gammaCS,eGammaCS,gammaCM,eGammaCM,gammaRate,eGammaRate,muCharge,eMuCharge,gammaCharge,eGammaCharge,tot,eTot; 
    
    

    //
    vector<float> vEff, vErrEff;
    float hvEff,eHVeff,iMon,eImon,hvMon,eHVmon;
    vector<float> vHvEff, vEHVEff, vImon, vEImon, vHvmon, vEHVmon;

    bool test = true;
    TH1D *testThr = new TH1D("testThr","testThr",100,0.,10.);
    TH1D *testBaseline = new TH1D("testBaseline","testBaseline",100,0.,10.);

	///////////
	// Muons //
	///////////
	double meanNoise = 0., muonPeak = 0., sq_sum = 0, stdev = 0, rms = 0, totMuonCharge = 0, muonChargePerStrip = 0, muonToT = 0;
	int eventsWitHit = 0, eventsWtihoutHit = 0, muonCounter = 0;
	bool muonEff[7] = {false,false,false,false,false,false,false}; //strip by strip efficiency
	bool isMuon = false, hasHitMuon = false;
	vector<float> muonPeakValue;
	vector<int> muonPeakPos;
	//TH1I *muonPeakTimeAllStrips = new TH1I("muonPeakTimeAllStrips","muonPeakTimeAllStrips",300,0.5,300.5);
	//TH1I *muonPeakTimePerStrip[7];
	//for (int i = 0; i < 7; i++) muonPeakTimePerStrip[i] = new TH1I(("muonStrips"+to_string(i+1)).c_str(),("muonStrips"+to_string(i+1)).c_str(),300,0.5,300.5);
	int clusSizeMuon = 1, clusMultMuon = 0;
	bool isClusMuon = false;
	vector<int> clustersMuon;
	TH1F *muonProfile = new TH1F("muonProfile","muonProfile",7,0.5,7.5); //muon strip profile
	TH1I *muonClusterMult = new TH1I("muonClusterMult","muonClusterMult",8,0.5,8.5); //muon cluster multiplicity
	TH1F *muonClusterSize = new TH1F("muonClusterSize","muonClusterSize",8,0.5,8.5); //muon cluster size
	TH1D *muonPromptCharge = new TH1D("muonPromptCharge","muonPromptCharge",20000,-0.5,2000.5); //muon prompt charge
	TH1D *hMuonToT[7]; //muon ToT per strip

	for (int i = 0; i < 7; i++) {
		hMuonToT[i] = new TH1D(("hMuonToT_"+to_string(i+1)).c_str(),("hMuonToT_"+to_string(i+1)).c_str(),1025,-0.5,1024.5);
	}
	//Test for max signal amplitude
	TH1F *signalMax = new TH1F("signalMax","signalMax",300,0,100);

	////////////
	// Gammas //
	////////////
	double meanNoiseGamma = 0., gammaPeak = 0., sq_sum_gamma = 0, stdevGamma = 0, rmsGamma = 0, totGammaCharge = 0, gammaChargePerStrip = 0, gammaToT = 0;
	int eventsWithGammaHit = 0, eventsWtihoutGammaHit = 0, gammaCounter = 0;
	bool gammaEff[7] = {false,false,false,false,false,false,false};
	bool isGamma = false, hasHitGamma = false;
	vector<float> gammaPeakValue;
	vector<int> gammaPeakPos, gammaCounts;
	//TH1I *gammaPeakTimeAllStrips = new TH1I("muonPeakTimeAllStrips","muonPeakTimeAllStrips",300,0.5,300.5);
	//TH1I *gammaPeakTimePerStrip[7];
	//for (int i = 0; i < 7; i++) gammaPeakTimePerStrip[i] = new TH1I(("gammaStrips"+to_string(i+1)).c_str(),("gammaStrips"+to_string(i+1)).c_str(),300,0.5,300.5);
	int clusSizeGamma = 1, clusMultGamma = 0;
	bool isClusGamma = false;
	vector<int> clustersGamma;
	TH1F *gammaProfile = new TH1F("gammaProfile","gammaProfile",7,0.5,7.5); //gamma strip profile
	TH1F *gammaRateProfile = new TH1F("gammaRateProfile","gammaRateProfile",7,0.5,7.5); //gamma rate profile
	TH1I *gammaClusterMult = new TH1I("gammaClusterMult","gammaClusterMult",8,0.5,8.5); //gamma cluster multiplicity
	TH1F *gammaClusterSize = new TH1F("gammaClusterSize","gammaClusterSize",8,0.5,8.5); //gamma cluster size
	TH1D *gammaPromptCharge = new TH1D("gammaPromptCharge","gammaPromptCharge",2000,-0.5,200.5); //gamma prompt charge
	TH1D *hGammaToT[7]; //gamma ToT per strip

    for (int i = 0; i < 7; i++) {
		hGammaToT[i] = new TH1D(("hGammaToT_"+to_string(i+1)).c_str(),("hGammaToT_"+to_string(i+1)).c_str(),1025,-0.5,1024.5);
	}

    //Loop on all HV points
    for (int i = 0; i < hvpoints; i++) {
    //for (int i = 6; i < 7; i++) {
        
        string hvPoint = scanFolder + "HV_" + to_string(i+1);

        cout << endl << "Analyzing HV value: " << i+1 << " in folder: " << hvPoint << endl;
	    bool graphMakeMuon = false, graphMakeGamma = false;

        //Open root file and get the tree inside
	    gSystem->cd(hvPoint.c_str());

        TFile *fout = new TFile(("HV_" + to_string(i+1) + "_ANALYSIS.root").c_str(),"RECREATE");
        TDirectory *dirEff = fout->mkdir("efficientEvents"); //Efficient muon events display
        TDirectory *dirNonEff = fout->mkdir("nonEfficientEvents"); //Non efficient muon events display
        TDirectory *dirEffGamma = fout->mkdir("gammaEfficientEvents"); //Efficient gamma events display
        TDirectory *dirNonEffGamma = fout->mkdir("gammaNonEfficientEvents");//Non efficient gamma events display

        TFile *f = new TFile(("digitizerData_HV_" + to_string(i+1) + ".root").c_str(),"READ");
        TTree *t = (TTree*)f->Get("dataTree");

        int nEntries = t->GetEntries();
        cout << "Number of entries in the tree: " << nEntries << endl;

        vector<float> *data[8] = {0,0,0,0,0,0,0,0};
        vector<float> datamV[8];
        //vector<float> gammaValues[8];

        for (int i = 0; i < 8; i++) {
            //gammaValues[i].reserve(1024*12502);
            datamV[i].reserve(1024);
        }
        
        vector<float> stripmV;

        if (verbose) for (unsigned int i = 0; i < times.size(); i++) cout << times.at(i) << endl;

        TCanvas *cStrip = new TCanvas(); //mV(time) for muons, eight per event
        cStrip->cd();
        cStrip->Divide(1,file_count);
        TCanvas *cStripGamma = new TCanvas(); //mV(time) for gammas, eight per event
        cStripGamma->cd();
        cStripGamma->Divide(1,file_count);
        TCanvas *cStripGammaTot = new TCanvas(); //mV(time) for gammas, eight in total, joined data from each event
        cStripGammaTot->cd();
        cStripGammaTot->Divide(1,file_count);

        TGraph *gStrip[file_count];
        TGraph *gStripGamma[file_count];
        TGraph *gStripGammaTot[file_count];
        TLine *noiseLine[file_count];
        TLine *minusNoiseLine[file_count];
        TMarker *peak[file_count];

        //Set Branch addresses for the 8 strips
        for (int i = 0; i < file_count; i++) {
            string branchName = "counts_strip_" + to_string(i);
            t->SetBranchAddress(branchName.c_str(),&data[i]);
            if (verbose) cout << "Setting branch address for: " << branchName << endl;
        }

        //Loop on all triggers of a given HV point
        for (int j = 0; j < nEntries; j++) {

            t->GetEntry(j); //get the j-th entry
            if (verbose2) cout << "Getting entry: " << j << endl;

            ////////////////
            // Muon event //
            ////////////////

            //Check if the event is muon or gamma by looking at the trigger (on channel 0)
            if (*min_element(data[0]->begin(), data[0]->end()) < 1500.) { //It's a muon - 1 Gs/s, if 5 Gs/s comment this line
                //if (graphMakeMuon == false) continue;
                muonCounter++;
                if (verbose2 && !isMuon) cout << "Event " << j << " is muon" << endl;
                isMuon = true;

                //Loop on all strips in a muon event
                for (int k = 0; k < file_count; k++) {

                    //Conversion to mV 
                    //Calculate mean oscillations, subtract to each point and convert to mV
                    meanNoise = accumulate(&data[k]->at(noiseMin), &data[k]->at(noiseMax), 0.0) / (noiseMax-noiseMin);
                    
                    for (unsigned int l = 0; l < data[0]->size(); l++) {
                        datamV[k].push_back((data[k]->at(l)-meanNoise)*convFactor); //CONVERSION HERE
                    }
                
                    //RMS (mV) -> Remember that inner_production function is [....) meaning that last element is not included in the calculation
                    sq_sum = inner_product(&datamV[k].at(noiseMin), &datamV[k].at(noiseMax), &datamV[k].at(noiseMin),0.0);
                    rms = std::sqrt(sq_sum/(noiseMax - noiseMin));

                    if (test == true) {
					    testThr->Fill(5*rms);
					    testBaseline->Fill(accumulate(&datamV[k].at(noiseMin), &datamV[k].at(noiseMax), 0.0) / (noiseMax-noiseMin));
				    }

                    //Plot event
                    if (graphMakeMuon) {
                        //gStrip[k] = new TGraph(data[k]->size(),&times[0],&data[k]->at(0)); //ADC counts
                        gStrip[k] = new TGraph(sampNumber,&times[0],&datamV[k][0]); //mV
                        gStrip[k]->GetXaxis()->SetLabelSize(0.1);
                        gStrip[k]->GetXaxis()->SetTickSize(0.01);
                        gStrip[k]->GetYaxis()->SetNdivisions(510);
                        gStrip[k]->GetYaxis()->SetRangeUser(-20*rms,20*rms);
                        gStrip[k]->GetYaxis()->SetLabelSize(0.1);
                        gStrip[k]->GetYaxis()->SetTickSize(0.01);
                        gStrip[k]->GetYaxis()->SetNdivisions(2);
                        gStrip[k]->SetMarkerColor(kRed);
                        gStrip[k]->SetLineColor(kRed);
                        gStrip[k]->SetTitle("");
                        cStrip->cd(k+1);
                        gStrip[k]->Draw("APL");
                        //noiseLine[k] = new TLine(times.front(),meanNoise + numberOfSigmas*stdev,times.back(),meanNoise + numberOfSigmas*stdev); //ADC counts
                        noiseLine[k] = new TLine(0,numberOfSigmas*rms,1024,numberOfSigmas*rms); //mV
                        minusNoiseLine[k] = new TLine(0,-numberOfSigmas*rms,1024,-numberOfSigmas*rms);
                        noiseLine[k]->SetLineColor(kBlue);
                        minusNoiseLine[k]->SetLineColor(kBlue);
                        noiseLine[k]->Draw("SAME");
                        minusNoiseLine[k]->Draw("SAME");
			    	}

                    //Trigger event, simply draw it and continue
                    if (k == 0) { 						
					    datamV[k].clear();
					    continue;
				    }

                    //Is the event efficient?
                    //Value corresponding to muon peak
				    //muonPeak = *min_element(&data[k]->at(muonMin), &data[k]->at(muonMax)); //Min in muon window - Negative pulse polarity - ADC counts
				    //muonPeak = *max_element(&data[k]->at(muonMin), &data[k]->at(muonMax)); //Max in muon window - Positive pule polarity - ADC counts
				    //muonPeak = *min_element(&datamV[k]->at(muonMin), &datamV[k]->at(muonMax)); //Min in muon window - Negative pulse polarity - mV
				    muonPeak = *max_element(&datamV[k].at(muonMin), &datamV[k].at(muonMax)); //Max in muon window - Positive pule polarity - mV

				    if (verbose) {
					    cout << "Event: \t" << j << "\t strip: \t" << k+1 << "\t muon pulse: \t" << muonPeak << "\t noise (with 5 sigma): \t" << numberOfSigmas*rms << endl; //Positive pulse polarity
				    }

				    //Was the chamber efficient?
                    //if (muonEff[k-1] == false && muonPeak <= (meanNoise - numberOfSigmas*stdev)) { //Negative pulse polarity - ADC counts
                    //if (muonEff[k-1] == false && muonPeak >= (meanNoise + numberOfSigmas*stdev)) { //Positive pulse polarity - ADC counts
                    //if (muonEff[k-1] == false && muonPeak <= threshold) { //FEERIC equivalent negative threshold - mV
                    //if (muonEff[k-1] == false && muonPeak >= threshold) { //FEERIC equivalent positive threshold - mV
                    //if (muonEff[k-1] == false && muonPeak <= numberOfSigmas*rms) { //Negative pulse polarity - mV
                    if (muonEff[k-1] == false && muonPeak >= numberOfSigmas*rms) { //Positive pulse polarity - mV

                        signalMax->Fill(muonPeak);
                        
                        //Test
                        muonEff[k-1] = true;

                        if (hasHitMuon == false) {
                            hasHitMuon = true;
                            //totMuonCharge = 0;
                            //muonChargePerStrip = 0;
                        }
                    }//End of if the strip is efficient 

                    else { //not efficient
                        muonEff[k-1] = false;
                    }

                    meanNoise = 0.;
                    muonPeak = 0.;
                    sq_sum = 0.;
                    stdev = 0.;
                    datamV[k].clear();

                }//End of loop on all strips

            } //End if muon

            /////////////////
            // Gamma event //
            /////////////////

            else { //It's a rate event
                
                gammaCounter++;
                if (verbose2 && !isGamma) cout << "Event " << j << " is gamma" << endl;
			    isGamma = true;
                
                for (int k = 0; k < file_count; k++) {
                    meanNoiseGamma = 0;
                    sq_sum_gamma = 0;
                    stdevGamma = 0;

                    meanNoiseGamma = accumulate(&data[k]->at(noiseMin), &data[k]->at(noiseMax), 0.0) / (noiseMax-noiseMin);
                    //cout << "Noise gamma " << meanNoiseGamma << endl;
                    //meanNoiseGamma = accumulate(&data[k]->at(0), &data[k]->at(150), 0.0) / (150);
                    
                    for (unsigned int z = 0; z < sampNumber; z++) {
                        datamV[k].push_back((data[k]->at(z)-meanNoiseGamma)*convFactor); //CONVERSION HERE
                    }

                    //STD DEV (ADC counts)
                    //sq_sum_gamma = inner_product(&data[k]->at(noiseMin), &data[k]->at(noiseMax), &data[k]->at(noiseMin),0.0);
                    //stdevGamma = std::sqrt(sq_sum_gamma/(noiseMax-noiseMin) - meanNoiseGamma*meanNoiseGamma); //std dev in noise window
                    
                    //RMS (mV) -> Remember that inner_production function is [....) meaning that last element is not included in the calculation
                    sq_sum_gamma = inner_product(&datamV[k].at(noiseMin), &datamV[k].at(noiseMax), &datamV[k].at(noiseMin),0.0);
                    rmsGamma = std::sqrt(sq_sum_gamma/(noiseMax-noiseMin)); //RMS in noise window;

                    if (test == true) {
					    testThr->Fill(5*rmsGamma);
					    testBaseline->Fill(accumulate(&datamV[k].at(noiseMin), &datamV[k].at(noiseMax), 0.0) / (noiseMax-noiseMin));
				    }

                    //sq_sum_gamma = inner_product(&datamV[k].at(0), &datamV[k].at(150), &datamV[k].at(0),0.0);
                    //rmsGamma = std::sqrt(sq_sum_gamma/(150)); //RMS in noise window;

                    //Draw gamma event
                    if (graphMakeGamma) {
                        //gStripGamma[k] = new TGraph(sampNumber,&times[0],&data[k]->at(0)); //ADC counts
                        gStripGamma[k] = new TGraph(sampNumber,&times[0],&datamV[k][0]); //mV
                        gStripGamma[k]->GetXaxis()->SetLabelSize(0.1);
                        gStripGamma[k]->GetXaxis()->SetTickSize(0.01);
                        gStripGamma[k]->GetYaxis()->SetNdivisions(510);
                        gStripGamma[k]->GetYaxis()->SetLabelSize(0.1);
                        gStripGamma[k]->GetYaxis()->SetTickSize(0.01);
                        gStripGamma[k]->GetYaxis()->SetNdivisions(2);
                        gStripGamma[k]->GetYaxis()->SetRangeUser(-20*rmsGamma,20*rmsGamma);
                        gStripGamma[k]->SetMarkerColor(kRed);
                        gStripGamma[k]->SetLineColor(kRed);
                        gStripGamma[k]->SetTitle("");
                        cStripGamma->cd(k+1);
                        gStripGamma[k]->Draw("APL");
                        //noiseLine[k] = new TLine(0,meanNoiseGamma + numberOfSigmas*stdevGamma,1024,meanNoiseGamma + numberOfSigmas*stdevGamma); //ADC counts
                        noiseLine[k] = new TLine(0,numberOfSigmas*rmsGamma,1024,numberOfSigmas*rmsGamma); //mV
                        minusNoiseLine[k] = new TLine(0,-numberOfSigmas*rmsGamma,1024,-numberOfSigmas*rmsGamma); //mV
                        noiseLine[k]->SetLineColor(kBlack);
                        minusNoiseLine[k]->SetLineColor(kBlack);
                        noiseLine[k]->Draw("SAME");
                        minusNoiseLine[k]->Draw("SAME");
                    }
                    
                    if (k == 0) { //Strip 0 is the int+ext coincidence, draw it but nothing will appear because there is no coincidence in a gamma event
                        datamV[k].clear();
                        continue;
                    }

                    //Is the event efficient?
                    //Value corresponding to gamma peak
				    //gammaPeak = *min_element(&data[k]->at(0), &data[k]->at(1024)); //Min in muon window - Negative pulse polarity - ADC counts
				    //gammaPeak = *max_element(&data[k]->at(0), &data[k]->at(1024)); //Max in muon window - Positive pule polarity - ADC counts
				    //gammaPeak = *min_element(&datamV[k]->at(0), &datamV[k]->at(1024)); //Min in muon window - Negative pulse polarity - mV
				    gammaPeak = *max_element(&datamV[k].at(0), &datamV[k].at(1023)); //Max in muon window - Positive pule polarity - mV

				    if (verbose) {
					    cout << "Event: \t" << j << "\t strip: \t" << k+1 << "\t gamma pulse: \t" << gammaPeak << "\t noise (with 5 sigma): \t" << numberOfSigmas*rmsGamma << endl; //Positive pulse polarity
				    }

				    //Was the chamber efficient?
                    //if (gammaEff[k-1] == false && gammaPeak <= (meanNoise - numberOfSigmas*stdev)) { //Negative pulse polarity - ADC counts
                    //if (gammaEff[k-1] == false && gammaPeak >= (meanNoise + numberOfSigmas*stdev)) { //Positive pulse polarity - ADC counts
                    //if (gammaEff[k-1] == false && gammaPeak <= threshold) { //FEERIC equivalent negative threshold - mV
                    //if (gammaEff[k-1] == false && gammaPeak >= threshold) { //FEERIC equivalent positive threshold - mV
                    //if (gammaEff[k-1] == false && gammaPeak <= numberOfSigmas*rmsGamma) { //Negative pulse polarity - mV
                    if (gammaEff[k-1] == false && gammaPeak >= numberOfSigmas*rmsGamma) { //Positive pulse polarity - mV
                        //signalMax->Fill(gammaPeak);
                        gammaEff[k-1] = true;
                        if (hasHitGamma == false) {
                            hasHitGamma = true;
                            //totGammaCharge = 0;
                            //gammaChargePerStrip = 0;
                        }
                    }//End of if the strip is efficient 

                    else { //not efficient
                        gammaEff[k-1] = false;
                    }

                    datamV[k].clear();
                }// End loop on gamma strips

            }//End if gamma

            if (isMuon == true) { //it's a muon event
			    isMuon = false;

			    if (hasHitMuon == true) { //at least one strip saw a muon
				    muonPromptCharge->Fill(totMuonCharge); //Fill charge histogram with sum of charges in all strips
				    hasHitMuon = false;
				    eventsWitHit++;

                    if (graphMakeMuon) {
					    fout->cd();
					    dirEff->cd();
					    cStrip->Write(("Event_"+to_string(j)).c_str());
				    }

                    for (int s = 0; s < 7; s++) {
					    if (muonEff[s] == true) {
						    muonEff[s] = false; //reset counters for next event
						    muonProfile->Fill(s+1,1); //fill muon strip profile strip by strip
					    }
				    }
                }

                else if (hasHitMuon == false) { //no strip saw a muon
				    eventsWtihoutHit++;
                    if (graphMakeMuon) { 
                        fout->cd();
                        dirNonEff->cd();
                        cStrip->Write(("Event_"+to_string(j)).c_str());
                    }
			    }
            } //End if isMuon == true

            else if (isGamma == true) { //it's a gamma event
			    isGamma = false;

			    if(hasHitGamma == true) {
				    hasHitGamma = false;
				    eventsWithGammaHit++;
				    if (graphMakeGamma) { 
					    fout->cd();
					    dirEffGamma->cd();
					    cStripGamma->Write(("Event_"+to_string(j)).c_str());
				    }
				    for (int s = 0; s < 7; s++) {
					    if (gammaEff[s] == true) {
						    gammaEff[s] = false; //reset counters for next event	
						    gammaProfile->Fill(s+1,1);
					    }
				    }
                }

                else if (hasHitGamma == false) {
				    eventsWtihoutGammaHit++;
				    if (graphMakeGamma) {
					    fout->cd();
					    dirNonEffGamma->cd();
					    cStripGamma->Write(("Event_"+to_string(j)).c_str());
				    }
			    }
            }   

        } //End of loop on all triggers (j) of the i-th voltage point

        //Muon strip profile
        TCanvas *cMuonProfile = new TCanvas();
        cMuonProfile->cd();
        muonProfile->GetXaxis()->SetTitle("Strip number");
        muonProfile->GetYaxis()->SetTitle("Muon counts");
        muonProfile->GetYaxis()->SetRangeUser(0,muonProfile->GetMaximum()+(0.1*muonProfile->GetMaximum()));
        muonProfile->Draw("HISTO");

        //Gamma strip profile
        TCanvas *cGammaProfile = new TCanvas();
        cGammaProfile->cd();
        gammaProfile->GetXaxis()->SetTitle("Strip number");
        gammaProfile->GetYaxis()->SetTitle("Gamma counts");
        gammaProfile->GetYaxis()->SetRangeUser(0,gammaProfile->GetMaximum()+(0.1*gammaProfile->GetMaximum()));
        gammaProfile->Draw("HISTO");

        //Threshold
        TCanvas *cThr = new TCanvas();
        cThr->cd();
        testThr->GetXaxis()->SetTitle("Threshold [mV]");
        testThr->GetYaxis()->SetTitle("Counts");
        testThr->GetYaxis()->SetRangeUser(0,testThr->GetMaximum()+(0.1*testThr->GetMaximum()));
        testThr->Draw("HISTO");

        //Baseline
        TCanvas *cBaseline = new TCanvas();
        cBaseline->cd();
        testBaseline->GetXaxis()->SetTitle("Baseline [mV]");
        testBaseline->GetYaxis()->SetTitle("Counts");
        testBaseline->GetYaxis()->SetRangeUser(0,testBaseline->GetMaximum()+(0.1*testBaseline->GetMaximum()));
        testBaseline->Draw("HISTO");

        cout << "Muon counter: " << muonCounter << " efficient events: " << eventsWitHit << " non efficient :" << eventsWtihoutHit << " efficiency: " << eventsWitHit/(double)muonCounter << endl;
        cout << "Gamma counter: " << gammaCounter << endl;

	    double eff = (eventsWitHit/(double)muonCounter)*100; //muon efficiency
	    double eEff = TMath::Sqrt((eff*(100-eff))/muonCounter); //error on muon efficiency

        muonCounter = 0;
        eventsWitHit = 0;
        eventsWtihoutHit = 0;

        vEff.push_back(eff);
        vErrEff.push_back(eEff);

        //Read CAEN parameters from .root CAEN file
        caenParam = hvReader(hvPoint, run, i+1);
        hvEff = get<0>(caenParam);
        vHvEff.push_back(hvEff);
        eHVeff = get<1>(caenParam);
        vEHVEff.push_back(eHVeff);
        iMon = get<2>(caenParam);
        vImon.push_back(iMon);
        eImon = get<3>(caenParam);
        vEImon.push_back(eImon);
        hvMon = get<4>(caenParam);
        vHvmon.push_back(hvMon);
        eHVmon = get<5>(caenParam);
        vEHVmon.push_back(eHVmon);
        
        fout->cd();
        cBaseline->Write(("Baseline_HV_" + to_string(i+1)).c_str());
        cThr->Write(("Threshold_HV_" + to_string(i+1)).c_str());
        cMuonProfile->Write(("Muon_profile_HV_" + to_string(i+1)).c_str());
        cGammaProfile->Write(("Muon_profile_HV_" + to_string(i+1)).c_str());
        fout->Close();

    } //End of loop on all HV points of the scan

    
    //Fit function for eff(HV) curve + set param limits and names
   	fit_eff = new TF1("fit_eff","[0]/(1+TMath::Exp(-[1]*(x-[2])))",vHvEff.front(),vHvEff.back());

	fit_eff->SetParLimits(0,45.,110.);
	//fit_eff->SetParLimits(1,0.,0.5);
	//fit_eff->SetParLimits(2,9900.,11000.);

	double effmax = fit_eff->GetParameter(0); //Max efficiency
	double lambda = fit_eff->GetParameter(1); //Lambda parameter
	double HV50 = fit_eff->GetParameter(2); //HV for 50% eff

    //Plot efficiency(HV) curve
    TCanvas *cEff = new TCanvas();
    cEff->cd();
    TGraphErrors *effHv = new TGraphErrors(vHvEff.size(),&vHvEff[0],&vEff[0],NULL,&vErrEff[0]);
    effHv->SetMarkerStyle(8);
    effHv->SetMarkerSize(1.4);
    effHv->GetXaxis()->SetTitle("HV_{eff} [V]");
    effHv->GetYaxis()->SetTitle("Eff [%]");
    effHv->GetYaxis()->SetRangeUser(0,100);
    effHv->Fit(fit_eff,"RM+");
    effHv->Draw("AP");

    double WP = (TMath::Log(19)/lambda)+HV50+150; //WP with CMS definition
	double effwp = fit_eff->Eval(WP); //Efficiency at WP

    //Plot I(HV) curve
    TCanvas *cCurr = new TCanvas();
    cCurr->cd();
    TGraphErrors *currHv = new TGraphErrors(vImon.size(),&vHvEff[0],&vImon[0],&vEHVEff[0],&vEImon[0]);
    currHv->SetMarkerStyle(8);
    currHv->SetMarkerSize(1);
    currHv->GetXaxis()->SetTitle("HV_{eff} [V]");
    currHv->GetYaxis()->SetTitle("I [#muA]");
    currHv->GetYaxis()->SetRangeUser(vImon.front() - 0.1*vImon.front(),vImon.back() + 0.1*vImon.back());
    currHv->Draw("AP");

    TFile *fAnalysisOut = new TFile((scanFolder+"Analysis_run_"+to_string(run)+".root").c_str(),"RECREATE");
    fAnalysisOut->cd();
    cEff->Write(("Efficiency_run_"+to_string(run)).c_str());
    cCurr->Write(("Current_run_"+to_string(run)).c_str());
    fAnalysisOut->Close();

    cEff->SaveAs((scanFolder + "efficiencyCurve_scan_"+to_string(run)+".png").c_str());
    cCurr->SaveAs((scanFolder + "currentCurve_scan_"+to_string(run)+".png").c_str()); 

    //Plot muon CS(HV) curve
    /*TCanvas *cMuCS = new TCanvas();
    cMuCS->cd();
    TGraphErrors *muCsHv = new TGraphErrors(muCS.size(),&hvEff[0],&muCS[0],NULL,&eMuCS[0]);
    muCsHv->SetMarkerStyle(8);
    muCsHv->SetMarkerSize(1);
    muCsHv->GetXaxis()->SetTitle("HV_{eff} [V]");
    muCsHv->GetYaxis()->SetTitle("Muon Cluster Size [strips]");
    muCsHv->GetYaxis()->SetRangeUser(muCS.front() - 0.1*muCS.front(),muCS.back() + 0.1*muCS.back());
    muCsHv->Draw("AP");

    //Plot muon CM(HV) curve
    TCanvas *cMuCM = new TCanvas();
    cMuCM->cd();
    TGraphErrors *muCmHv = new TGraphErrors(muCM.size(),&hvEff[0],&muCM[0],NULL,&eMuCM[0]);
    muCmHv->SetMarkerStyle(8);
    muCmHv->SetMarkerSize(1);
    muCmHv->GetXaxis()->SetTitle("HV_{eff} [V]");
    muCmHv->GetYaxis()->SetTitle("Muon Cluster Multiplicity");
    muCmHv->GetYaxis()->SetRangeUser(muCM.front() - 0.1*muCM.front(),muCM.back() + 0.1*muCM.back());
    muCmHv->Draw("AP");

    //Plot gamma CS(HV) curve
    TCanvas *cGammaCS = new TCanvas();
    cGammaCS->cd();
    TGraphErrors *gammaCsHv = new TGraphErrors(gammaCS.size(),&hvEff[0],&gammaCS[0],NULL,&eGammaCS[0]);
    gammaCsHv->SetMarkerStyle(8);
    gammaCsHv->SetMarkerSize(1);
    gammaCsHv->GetXaxis()->SetTitle("HV_{eff} [V]");
    gammaCsHv->GetYaxis()->SetTitle("Gamma Cluster Size [strips]");
    gammaCsHv->GetYaxis()->SetRangeUser(gammaCS.front() - 0.1*gammaCS.front(),gammaCS.back() + 0.1*gammaCS.back());
    gammaCsHv->Draw("AP");

    //Plot gamma CM(HV) curve
    TCanvas *cGammaCM = new TCanvas();
    cGammaCM->cd();
    TGraphErrors *gammaCmHv = new TGraphErrors(gammaCM.size(),&hvEff[0],&gammaCM[0],NULL,&eGammaCM[0]);
    gammaCmHv->SetMarkerStyle(8);
    gammaCmHv->SetMarkerSize(1);
    gammaCmHv->GetXaxis()->SetTitle("HV_{eff} [V]");
    gammaCmHv->GetYaxis()->SetTitle("Gamma Cluster Multiplicity");
    gammaCmHv->GetYaxis()->SetRangeUser(gammaCM.front() - 0.1*gammaCM.front(),gammaCM.back() + 0.1*gammaCM.back());
    gammaCmHv->Draw("AP");

    //Plot gamma rate(HV) curve
    TCanvas *cGammaRate = new TCanvas();
    cGammaRate->cd();
    TGraphErrors *gammaRateHv = new TGraphErrors(gammaRate.size(),&hvEff[0],&gammaRate[0],NULL,&eGammaRate[0]);
    gammaRateHv->SetMarkerStyle(8);
    gammaRateHv->SetMarkerSize(1);
    gammaRateHv->GetXaxis()->SetTitle("HV_{eff} [V]");
    gammaRateHv->GetYaxis()->SetTitle("Gamma rate [Hz/cm^{2}]");
    gammaRateHv->GetYaxis()->SetRangeUser(gammaRate.front() - 0.1*gammaRate.front(),gammaRate.back() + 0.1*gammaRate.back());
    gammaRateHv->Draw("AP");

    //Plot muon prompt charge(HV) curve
    TCanvas *cMuCharge = new TCanvas();
    cMuCharge->cd();
    TGraphErrors *muChargeHv = new TGraphErrors(muCharge.size(),&hvEff[0],&muCharge[0],NULL,&eMuCharge[0]);
    muChargeHv->SetMarkerStyle(8);
    muChargeHv->SetMarkerSize(1);
    muChargeHv->GetXaxis()->SetTitle("HV_{eff} [V]");
    muChargeHv->GetYaxis()->SetTitle("Muon prompt charge [pC]");
    muChargeHv->GetYaxis()->SetRangeUser(muCharge.front() - 0.1*muCharge.front(),muCharge.back() + 0.1*muCharge.back());
    muChargeHv->Draw("AP");

    //Plot gamma prompt charge(HV) curve
    TCanvas *cGammaCharge = new TCanvas();
    cGammaCharge->cd();
    TGraphErrors *gammaChargeHv = new TGraphErrors(gammaCharge.size(),&hvEff[0],&gammaCharge[0],NULL,&eGammaCharge[0]);
    gammaChargeHv->SetMarkerStyle(8);
    gammaChargeHv->SetMarkerSize(1);
    gammaChargeHv->GetXaxis()->SetTitle("HV_{eff} [V]");
    gammaChargeHv->GetYaxis()->SetTitle("Gamma prompt charge [pC]");
    gammaChargeHv->GetYaxis()->SetRangeUser(gammaCharge.front() - 0.1*gammaCharge.front(),gammaCharge.back() + 0.1*gammaCharge.back());
    gammaChargeHv->Draw("AP");


    TFile *fAnalysisOut = new TFile(("Analysis_run_"+to_string(run)+".root").c_str(),"RECREATE");
    fAnalysisOut->cd();
    cEff->Write(("Efficiency_run_"+to_string(run)).c_str());
    cCurr->Write(("Current_run_"+to_string(run)).c_str());
    cMuCS->Write(("Muon_CS_run_"+to_string(run)).c_str());
    cMuCM->Write(("Muon_CM_run_"+to_string(run)).c_str());
    cGammaCS->Write(("Gamma_CS_run_"+to_string(run)).c_str());
    cGammaCM->Write(("Gamma_CM_run_"+to_string(run)).c_str());
    cGammaRate->Write(("Gamma_rate_run_"+to_string(run)).c_str());
    cMuCharge->Write(("Muon_prompt_charge_run_"+to_string(run)).c_str());
    cGammaCharge->Write(("Gamma_prompt_charge_run_"+to_string(run)).c_str());

    fAnalysisOut->Close();*/
}
