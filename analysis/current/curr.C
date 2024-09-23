//Root code to analyze current scan
//To execute enter root -> .x curr.C(run number) [for example .x curr.C(49)]

#include "TCanvas.h"
#include "Riostream.h"
#include "TGraph.h"
#include "TAxis.h"
#include "TMultiGraph.h"
#include "TLegend.h"
#include "TLine.h"
#include "TLatex.h"
#include "TMath.h"
#include "TPaveText.h"
#include "TFile.h"
#include <vector>
#include "TGraphErrors.h"
#include "TH1F.h"
#include "TSystem.h"
#include "TF1.h"
#include <algorithm> // std::min_element
#include <iterator>  // std::begin, std::end
#include <filesystem> //to count the number of folders in each scan

using namespace std;
using namespace TMath;

const char ext[20] =".root";
const int detNum = 1;

void curr(const int scan) {

	string folder = "/home/pcald32/runs/currentScans/scan_"+to_string(scan)+"/";
	
    gSystem->cd(folder.c_str());
    
    //count how many points there are in the scan by counting the number of folders
    int nfolders = 0; //number of folders in the scan = number of hv points
    for (auto const& dir+_entry :std::filesystem::directory_iterator{folder}) {
    	nfolders++;
    }

    //define vectors for HV and current in each scan
    vector <float> HVeff, HVapp, Imon;
    vector <float> eHVeff, eHVapp, eImon;
    double init_q, init_m = 0;
    
    for (int i = 0; i < nfolders; i++) {
        gSystem->cd((folder+"HV_"+to_string(i+1)).c_str());

        cout << "Entering folder " + folder+"HV_"+to_string(i+1) << endl;

        TFile *fin = new TFile(("scan_"+to_string(scan)+"_CAEN_HV"+to_string(i+1)+".root").c_str(),"READ");

        TH1F *hHVapp = (TH1F*)fin->Get(("--GIF_temp--_HV_app_"+to_string(i+1)).c_str());
        TH1F *hHVeff = (TH1F*)fin->Get(("--GIF_temp--_HV_eff_"+to_string(i+1)).c_str());
        TH1F *hHVmon = (TH1F*)fin->Get(("--GIF_temp--_HV_mon_"+to_string(i+1)).c_str());
        TH1F *hImon = (TH1F*)fin->Get(("--GIF_temp--_I_mon_"+to_string(i+1)).c_str());

        HVeff.push_back(hHVeff->GetMean());
        HVapp.push_back(hHVapp->GetMean());
        //Imon.push_back(hImon->GetMean()/2500);
        Imon.push_back(hImon->GetMean());

        eHVeff.push_back(hHVeff->GetMeanError());
        eHVapp.push_back(hHVapp->GetMeanError());
        //eImon.push_back(hImon->GetMeanError()/2500);
        eImon.push_back(hImon->GetMeanError());

        //gSystem->cd("/home/pcald32/runs/currentScans/scan_34");
    }

    sort(HVeff.begin(),HVeff.end());
    sort(eHVeff.begin(),eHVeff.end());
    sort(Imon.begin(),Imon.end());
    sort(eImon.begin(),eImon.end());

    TGraphErrors *IVcurve = new TGraphErrors(HVapp.size(),&HVeff[0],&Imon[0],&eHVeff[0],&eImon[0]);

    IVcurve->SetMarkerStyle(8);
    IVcurve->SetMarkerSize(2);
    IVcurve->SetTitle("I(V) curve");
    IVcurve->GetXaxis()->CenterTitle();
    IVcurve->GetYaxis()->CenterTitle();
    IVcurve->GetXaxis()->SetTitleFont(62);
    IVcurve->GetYaxis()->SetLabelFont(62);
    IVcurve->GetXaxis()->SetLabelFont(62);
    IVcurve->GetYaxis()->SetTitleFont(62);
    IVcurve->GetXaxis()->SetTitle("HV_{eff} [V]");
    IVcurve->GetYaxis()->SetTitle("I [#muA]");
    TCanvas *cDet = new TCanvas("","",1000,800);
    cDet->cd();
    IVcurve->Draw("AP");
}
