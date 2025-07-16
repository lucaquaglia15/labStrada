
#include "TTree.h"
#include "TBranch.h"
#include "TFile.h"
#include "TSystem.h"
#include "Riostream.h"
#include "TString.h"
#include "TMath.h"
#include <stdlib.h>
#include <fstream>
#include <numeric>
#include <vector>
#include <array>
#include <algorithm>
#include <string> 
#include <tuple>
//--------------------//
//                    //
//    Produce tree    //
//                    //
//--------------------//

void convert2root(string folderPath, string waveFile, int hv, bool verbose) {

    //Name of the input file
    string fileName;

	gSystem->cd(folderPath.c_str());
	if(verbose) cout << folderPath << endl;

	//TFile *fData = new TFile(("digitizerData_HV_" + to_string(hv+1) + ".root").c_str(),"RECREATE"); //root file to save data
	/*TFile *fData = new TFile(("digitizerData_HV_" + to_string(hv) + ".root").c_str(),"RECREATE"); //root file to save data
    TTree *dataTree = new TTree("dataTree","Data from digitizer"); //tree

    vector<vector<string>> data;
	vector<string> strip;
	vector<double> counts[8];

	for (int i = 0; i < 8; i++) {
		string branchName = "counts_strip_" + to_string(i);
		dataTree->Branch(branchName.c_str(), &counts[i]);
		if (verbose) cout << &(counts[i]) << endl;
	}*/

    vector<vector<string>> data;
	vector<string> strip;
	vector<double> counts[8];
	
    //string tp = ""; //new position
	for (int i = 0; i < 8; i++) {

		fstream dataFile; //For txt input file -> to stream data
		fileName = waveFile + to_string(i) + ".txt";
		dataFile.open(fileName.c_str());

		if (dataFile.is_open()) { //Open file and parse useful information to put in .root file
			if (verbose) cout << "Opening file: " << fileName << endl;
			string tp = ""; //old position, working

			while(getline(dataFile,tp)) {
				strip.push_back(tp);
			}
			data.push_back(strip);
			strip.clear();
		}

		else { //File opening not succesful, close the program
			cout << "Error in opening wave file" << endl;
			exit(1);
		}
		dataFile.close();
	}

	int counter = 0;

    //Moved here because I noticed that if the txt file is not there and you run the code by mistake this would delete the roo file and you would lose all the contents
	TFile *fData = new TFile(("digitizerData_HV_" + to_string(hv) + ".root").c_str(),"RECREATE"); //root file to save data
    TTree *dataTree = new TTree("dataTree","Data from digitizer"); //tree

	for (int i = 0; i < 8; i++) {
		string branchName = "counts_strip_" + to_string(i);
		dataTree->Branch(branchName.c_str(), &counts[i]);
		if (verbose) cout << &(counts[i]) << endl;
	}

	if (verbose) cout << data[0].size() << endl;

	for (unsigned int i = 0; i < data[0].size(); i++) {
		if ((i % 1032 >= 8 && i % 1032 <= 1031)) { //ADC data
			for (int j = 0; j < 8; j++) {
				counts[j].push_back(stod(data[j][i]));
				counter++;
				if (counter == 1024*8) { //event finished
					dataTree->Fill();
					counter = 0;
					for (unsigned k = 0; k < 8; k++) counts[k].clear();
				}
			}
		}
	} //<- WORKING VERSION!!! ->

	fData->cd();
	dataTree->Write();
	//dataTree->Write("", TObject::kOverwrite); //In theory this saves the data without creating the same tree twice (i.e. dataTree10, dataTree11)
	fData->Close();
}