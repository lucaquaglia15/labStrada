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

void res(const int scan, const string detector, const float primo_punto) {

	string folder = "/home/pcald32/runs/currentScans/scan_"+to_string(scan)+"/";
	
    gSystem->cd(folder.c_str());
    string extension = "ot";
    
    //count how many points there are in the scan by counting the number of folders
    int nfolders = 0; //number of folders in the scan = number of hv points
    for (auto const& dir_entry :std::filesystem::directory_iterator{folder}) {
        //str.compare(str.size() - suffix.size(), suffix.size(), suffix) == 0;
        string fol = std::filesystem::path(dir_entry).filename().string();
    	if(fol.compare(fol.size() - extension.size(), extension.size(), extension) != 0)
        nfolders++;
    }

    //define vectors for HV and current in each scan
    vector <float> HVeff, HVapp, Imon;
    vector <float> eHVeff, eHVapp, eImon;
    //double init_q, init_m = 0;
    
    for (int i = 0; i < nfolders; i++) {
        gSystem->cd((folder+"HV_"+to_string(i+1)).c_str());

        cout << "Entering folder " + folder+"HV_"+to_string(i+1) << endl;

        TFile *fin = new TFile(("scan_"+to_string(scan)+"_CAEN_HV"+to_string(i+1)+".root").c_str(),"READ");

        TH1F *hHVapp = (TH1F*)fin->Get((detector + "_HV_app_"+to_string(i+1)).c_str());
        TH1F *hHVeff = (TH1F*)fin->Get((detector + "_HV_eff_"+to_string(i+1)).c_str());
        TH1F *hHVmon = (TH1F*)fin->Get((detector + "_HV_mon_"+to_string(i+1)).c_str());
        TH1F *hImon = (TH1F*)fin->Get((detector + "_I_mon_"+to_string(i+1)).c_str());

        if (i >= 10 && scan == 51) {
            hHVapp = (TH1F*)fin->Get((detector + "_HV_app_"+to_string(i+1-10)).c_str());
            hHVeff = (TH1F*)fin->Get((detector + "_HV_eff_"+to_string(i+1-10)).c_str());
            hHVmon = (TH1F*)fin->Get((detector + "_HV_mon_"+to_string(i+1-10)).c_str());
            hImon = (TH1F*)fin->Get((detector + "_I_mon_"+to_string(i+1-10)).c_str());
        }

        HVeff.push_back(hHVeff->GetMean());
        HVapp.push_back(hHVapp->GetMean());
        //Imon.push_back(hImon->GetMean()/2500);
        Imon.push_back(hImon->GetMean());

        eHVeff.push_back(hHVeff->GetMeanError());
        eHVapp.push_back(hHVapp->GetMeanError());
        //eImon.push_back(hImon->GetMeanError()/2500);
        //eImon.push_back(hImon->GetMeanError());
        eImon.push_back(hImon->GetStdDev());
    }

    gSystem->cd(folder.c_str());

    sort(HVeff.begin(),HVeff.end());
    sort(eHVeff.begin(),eHVeff.end());
    sort(Imon.begin(),Imon.end());
    sort(eImon.begin(),eImon.end());

    TGraphErrors *IVcurve = new TGraphErrors(HVapp.size(),&HVeff[0],&Imon[0],&eHVeff[0],&eImon[0]);

    IVcurve->SetMarkerStyle(8);
    IVcurve->SetMarkerSize(2);
    IVcurve->SetTitle((detector + " I(HV) curve").c_str());
    IVcurve->GetXaxis()->CenterTitle();
    IVcurve->GetYaxis()->CenterTitle();
    IVcurve->GetXaxis()->SetTitleFont(62);
    IVcurve->GetYaxis()->SetLabelFont(62);
    IVcurve->GetXaxis()->SetLabelFont(62);
    IVcurve->GetYaxis()->SetTitleFont(62);
    IVcurve->GetXaxis()->SetTitle("HV_{eff} [V]");
    IVcurve->GetYaxis()->SetTitle("I [#muA]");

    //Faccio fit retta
    TF1 *f1= new TF1("f1","[0]*x + [1]",primo_punto,HVeff.back());
    IVcurve->Fit("f1","R");

    cout<< "Chi2: "<<f1->GetChisquare()<< endl;
    
    //calcolo la resistività 
    //R_1 è R alla -1
    float R= 1/(f1->GetParameter(0)); //[micro ohm]
    float eR= 1/pow(f1->GetParameter(0),2)*(f1->GetParError(0));//[micro ohm]
    cout<<"Il pannello "<< detector<< " ha una resistenza  R = "<<R<<" +- "<<eR<<" [micro ohm]"<<endl;

    float ro =R*pow(10,6)*2500/0.2; //[ohm]*[cm^2]/[cm]
    float e_ro= eR*pow(10,6)*2500/0.2;
    cout<<"La resistività calcolata è ro :"<<ro<<" +- "<<e_ro<< " [ohm*cm]"<<endl;
    
    
    TCanvas *cDet = new TCanvas("","",1000,800);
    cDet->cd();
    IVcurve->Draw("AP");

    TFile *Fout= new TFile(("outfile_"+detector+"_scan_"+to_string(scan)+".root").c_str(),"RECREATE");
    Fout->cd();
    cDet->Write(("IVcurve_"+detector).c_str());
    Fout->Close();


}
