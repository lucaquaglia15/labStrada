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

using namespace std;
using namespace TMath;

const char ext[20] =".root";
const int detNum = 1;

void res() {

    gSystem->cd("/home/pcald32/runs/currentScans/scan_12");

    //define vectors for HV and current in each scan
    vector <float> HVeff, HVapp, Imon;
    vector <float> eHVeff, eHVapp, eImon;
    double init_q, init_m = 0;
    
    for (int i = 0; i < 21; i++) {
        gSystem->cd(("/home/pcald32/runs/currentScans/scan_12/HV_"+to_string(i+1)).c_str());

        cout << "Entering folder /home/pcald32/runs/currentScans/scan_12/HV_"+to_string(i+1) << endl;

        TFile *fin = new TFile(("scan_12_CAEN_HV"+to_string(i+1)+".root").c_str(),"READ");

        TH1F *hHVapp = (TH1F*)fin->Get(("ECOgas_HV_app_"+to_string(i+1)).c_str());
        TH1F *hHVeff = (TH1F*)fin->Get(("ECOgas_HV_eff_"+to_string(i+1)).c_str());
        TH1F *hHVmon = (TH1F*)fin->Get(("ECOgas_HV_mon_"+to_string(i+1)).c_str());
        TH1F *hImon = (TH1F*)fin->Get(("ECOgas_I_mon_"+to_string(i+1)).c_str());

        HVeff.push_back(hHVeff->GetMean());
        HVapp.push_back(hHVapp->GetMean());
        Imon.push_back(hImon->GetMean());

        eHVeff.push_back(hHVeff->GetMeanError());
        eHVapp.push_back(hHVapp->GetMeanError());
        eImon.push_back(hImon->GetStdDev());

        gSystem->cd("/home/pcald32/runs/currentScans/scan_13");
    }

    sort(HVeff.begin(),HVeff.end());
    sort(eHVeff.begin(),eHVeff.end());
    sort(Imon.begin(),Imon.end());
    sort(eImon.begin(),eImon.end());
    
    auto minHV = std::min_element(std::begin(HVeff), std::end(HVeff));
    auto maxHV = std::max_element(std::begin(HVeff), std::end(HVeff));
    //if (std::end(HVeff)!=minHV)
        //std::cout << *minHV << '\n';
    
    TF1 *fit = new TF1("fit","[0]+[1]*x",2200,*maxHV);

    TGraphErrors *IVcurve = new TGraphErrors(HVapp.size(),&HVeff[0],&Imon[0],&eHVeff[0],&eImon[0]);

    fit->SetParameter(0,init_q);
    fit->SetParameter(1,init_m);
    IVcurve->Fit(fit,"MR+");
    double q = fit->GetParameter(0);
    double sigma_q = fit->GetParError(0);
    double m = fit->GetParameter(1);
    double sigma_m = fit->GetParError(1);
    double S = 2500;
    double h = 50;
    double b = 50;
    double eS = 0;
    double eh = 0.1;
    double eb = 0.1;
    double l = 0.4;
    double R = 0;
    double eR = 0;
    eS = Sqrt(pow((h*eb),2)+pow((b*eh),2));
    cout<<"Error of the RPC surface: "<<eS<<endl;
    R = (1/m);
    eR = sigma_m/pow(m,2);
    cout<<"The resistance is: "<<R<<"   "<<"The resistence error is: "<<eR<<endl;
    double rho = 0;
    rho = (S*R)/l;
    double erho = 0;
    erho = Sqrt((pow(((S*sigma_m)/(l*pow(m,2))),2))+(pow(((R*1.4)/l),2))+(pow(((R*S*0.1)/pow(l,2)),2)));
    cout<<"The resistivity is: "<<rho<<"    "<<"The resitivity error is: "<<erho<<endl;

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
