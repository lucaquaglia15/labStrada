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
#include "TMultiGraph.h"
#include "TH1F.h"
#include "TSystem.h"
#include "TF1.h"
#include <algorithm> // std::min_element
#include <iterator>  // std::begin, std::end

using namespace std;
using namespace TMath;

const char ext[20] =".root";
const int detNum = 1;

void currMulti() {

	vector <int> scan = {34,35,37,38,39,40};
    int scanNum = 0;
    TGraph *gIV[6];
    for (int l = 0; l<scan.size(); l++) {
        scanNum = scan.at(l);
        string folder = "/home/pcald32/runs/currentScans/scan_"+to_string(scanNum)+"/";
        gSystem->cd(folder.c_str());
        //define vectors for HV and current in each scan
        vector <float> HVeff, HVapp, Imon;
        vector <float> eHVeff, eHVapp, eImon;
        double init_q, init_m = 0;
        if (scan[l]==34||scan[l]==35||scan[l]==37||scan[l]==38) {
            for (int i = 0; i < 13; i++) {
                gSystem->cd((folder+"HV_"+to_string(i+1)).c_str());

                cout << "Entering folder " + folder+"HV_"+to_string(i+1) << endl;

                TFile *fin = new TFile(("scan_"+to_string(scanNum)+"_CAEN_HV"+to_string(i+1)+".root").c_str(),"READ");

                TH1F *hHVapp = (TH1F*)fin->Get(("--GIF_temp--_HV_app_"+to_string(i+1)).c_str());
                TH1F *hHVeff = (TH1F*)fin->Get(("--GIF_temp--_HV_eff_"+to_string(i+1)).c_str());
                TH1F *hHVmon = (TH1F*)fin->Get(("--GIF_temp--_HV_mon_"+to_string(i+1)).c_str());
                TH1F *hImon = (TH1F*)fin->Get(("--GIF_temp--_I_mon_"+to_string(i+1)).c_str());

                HVeff.push_back(hHVeff->GetMean());
                HVapp.push_back(hHVapp->GetMean());
                Imon.push_back(hImon->GetMean()/2500);

                eHVeff.push_back(hHVeff->GetMeanError());
                eHVapp.push_back(hHVapp->GetMeanError());
                eImon.push_back(hImon->GetMeanError()/2500);
            }
            sort(HVeff.begin(),HVeff.end());
            sort(eHVeff.begin(),eHVeff.end());
            sort(Imon.begin(),Imon.end());
            sort(eImon.begin(),eImon.end());
            //cout<<"Sto ordinando gli elementi"<<endl;
            gIV[l] = new TGraphErrors(HVapp.size(),&HVeff[0],&Imon[0],&eHVeff[0],&eImon[0]);
            gIV[l]->SetMarkerSize(2);
            gIV[l]->SetTitle("I(V) curve");
            gIV[l]->GetXaxis()->CenterTitle();
            gIV[l]->GetYaxis()->CenterTitle();
            gIV[l]->GetXaxis()->SetTitleFont(62);
            gIV[l]->GetYaxis()->SetLabelFont(62);
            gIV[l]->GetXaxis()->SetLabelFont(62);
            gIV[l]->GetYaxis()->SetTitleFont(62);
            //cout<<"Ho fatto i primi grafici"<<endl;
        }
        else if (scan[l]==39) {
            for (int i = 0; i < 12; i++) {
                gSystem->cd((folder+"HV_"+to_string(i+1)).c_str());

                cout << "Entering folder " + folder+"HV_"+to_string(i+1) << endl;

                TFile *fin = new TFile(("scan_"+to_string(scanNum)+"_CAEN_HV"+to_string(i+1)+".root").c_str(),"READ");
                //cout<<"Sono entrato nella cartella scan 38"<<endl;
                TH1F *hHVapp = (TH1F*)fin->Get(("--GIF_temp--_HV_app_"+to_string(i+1)).c_str());
                TH1F *hHVeff = (TH1F*)fin->Get(("--GIF_temp--_HV_eff_"+to_string(i+1)).c_str());
                TH1F *hHVmon = (TH1F*)fin->Get(("--GIF_temp--_HV_mon_"+to_string(i+1)).c_str());
                TH1F *hImon = (TH1F*)fin->Get(("--GIF_temp--_I_mon_"+to_string(i+1)).c_str());

                HVeff.push_back(hHVeff->GetMean());
                HVapp.push_back(hHVapp->GetMean());
                Imon.push_back(hImon->GetMean()/2500);

                eHVeff.push_back(hHVeff->GetMeanError());
                eHVapp.push_back(hHVapp->GetMeanError());
                eImon.push_back(hImon->GetMeanError()/2500);
            }
            sort(HVeff.begin(),HVeff.end());
            sort(eHVeff.begin(),eHVeff.end());
            sort(Imon.begin(),Imon.end());
            sort(eImon.begin(),eImon.end());
            gIV[l] = new TGraphErrors(HVapp.size(),&HVeff[0],&Imon[0],&eHVeff[0],&eImon[0]);
            gIV[l]->SetMarkerSize(2);
            gIV[l]->SetTitle("I(V) curve");
            gIV[l]->GetXaxis()->CenterTitle();
            gIV[l]->GetYaxis()->CenterTitle();
            gIV[l]->GetXaxis()->SetTitleFont(62);
            gIV[l]->GetYaxis()->SetLabelFont(62);
            gIV[l]->GetXaxis()->SetLabelFont(62);
            gIV[l]->GetYaxis()->SetTitleFont(62);
        }
        else if (scan[l]==690) {
            for (int i = 0; i < 6; i++) {

                TFile *fin = new TFile(("Scan000690_HV"+to_string(i+1)+"_CAEN.root").c_str(),"READ");
                
                TH1F *hHVapp = (TH1F*)fin->Get("HVapp_ALICE-2-0");
                TH1F *hHVeff = (TH1F*)fin->Get("HVeff_ALICE-2-0");
                TH1F *hHVmon = (TH1F*)fin->Get("HVmon_ALICE-2-0");
                TH1F *hImon = (TH1F*)fin->Get("Imon_ALICE-2-0");


                HVeff.push_back(hHVeff->GetMean());
                HVapp.push_back(hHVapp->GetMean());
                Imon.push_back(hImon->GetMean()/2500);
                

                eHVeff.push_back(hHVeff->GetMeanError());
                eHVapp.push_back(hHVapp->GetMeanError());
                eImon.push_back(hImon->GetMeanError()/2500);
                cout<<"Ho riempito i vettori"<<endl;
            }
            sort(HVeff.begin(),HVeff.end());
            sort(eHVeff.begin(),eHVeff.end());
            sort(Imon.begin(),Imon.end());
            sort(eImon.begin(),eImon.end());
            gIV[l] = new TGraphErrors(HVapp.size(),&HVeff[0],&Imon[0],&eHVeff[0],&eImon[0]);
            gIV[l]->SetMarkerSize(2);
            gIV[l]->SetTitle("I(V) curve");
            gIV[l]->GetXaxis()->CenterTitle();
            gIV[l]->GetYaxis()->CenterTitle();
            gIV[l]->GetXaxis()->SetTitleFont(62);
            gIV[l]->GetYaxis()->SetLabelFont(62);
            gIV[l]->GetXaxis()->SetLabelFont(62);
            gIV[l]->GetYaxis()->SetTitleFont(62);
        }
    }

    
    
	gIV[0]->SetMarkerStyle(69);
    gIV[1]->SetMarkerStyle(71);
    gIV[2]->SetMarkerStyle(72);
    gIV[3]->SetMarkerStyle(73);
    gIV[4]->SetMarkerStyle(76);
    gIV[5]->SetMarkerStyle(84);
    gIV[5]->SetMarkerColor(2);
    
    auto cIV = new TCanvas("","",1200,1200);
    cIV->SetGridx();
    cIV->SetGridy();
    gPad->SetTopMargin(0.02);
    gPad->SetRightMargin(0.02);
    gPad->SetLeftMargin(0.1);
    cIV->cd();
     TMultiGraph* mg = new TMultiGraph();
    for (int k=0; k<6; k++) {
      mg->Add(gIV[k]);
    }
    mg->GetXaxis()->SetTitle("HV_{eff} [V]");
    mg->GetYaxis()->SetTitle("Current density [#muA/cm^{2}]");
    mg->GetXaxis()->CenterTitle(true);
    mg->GetYaxis()->CenterTitle(true);
    mg->GetXaxis()->SetTitleFont(62);
    mg->GetYaxis()->SetTitleFont(62);
    mg->GetXaxis()->SetLabelFont(62);
    mg->GetYaxis()->SetLabelFont(62);
    mg->GetYaxis()->SetTitleOffset(1.55);
    
    mg->Draw("ap");
    
    auto legend = new TLegend(0.22,0.81,0.40,0.91);
    //legend->SetHeader("Legend","C"); // option "C" allows to center the header
    legend->SetBorderSize(0); //No borders in legend
	legend->SetFillStyle(0); //Transparent background
	legend->SetTextFont(62); //Bold legend
    legend->SetTextSize(0.02);
    legend->AddEntry(gIV[0],"ECO2 no flow for 24 days","p");
    legend->AddEntry(gIV[1],"ECO2 no flow for 25 days","p");
    legend->AddEntry(gIV[2],"STD mixture no SF6 after 7.5 volume changes","p");
    legend->AddEntry(gIV[3],"STD mixture no SF6 after 12 volume changes","p");
    legend->AddEntry(gIV[4],"STD mixture with SF6 after 12 volume changes","p");
    legend->AddEntry(gIV[5],"Last GIF++ scan","p");
    legend->Draw();
   

}
