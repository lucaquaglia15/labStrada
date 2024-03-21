 // PER-USER SETTINGS //

#define TEST_FILE_NAME "test__martino.las"			// NB Needs to be 17 chars
#define HIST_TEMPFILE_NAME "hist_sta_tino.las"		// NB Needs to be 17 chars
#define HIST_ANAL_TO_HIST_STANDARD "cp hist_anal_tino.las hist_sta_tino.las"

/*
#define USER_OUTFILE "/home/daq/analisi/histos/run%d-tino.txt"
#define USER_ROOTFILE "/home/daq/analisi/histos/analisi_%d-tino.root"
#define USER_EFFFILE "/home/daq/analisi/effcells/effcells_%d.out"
*/

#define USER_OUTFILE "run%03d-tino.txt"
#define USER_ROOTFILE "analisi_%03d-tino.root"
#define USER_EFFFILE "effcells_%03d.out"


#include <fstream>
#include <iostream>
#include <iomanip>

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <malloc.h>
#include <stdint.h>

#include "rhisto2.h"

#include <unistd.h>
#include <ctype.h>
#include <math.h> 	// To use function fabs() : float absolute value

//#include "monitor.h"
//#include "event2.h"


#include "/usr/local/root/include/TROOT.h"
#include "/usr/local/root/include/TFile.h"
#include "/usr/local/root/include/TH1.h"
#include "/usr/local/root/include/TH2.h"
#include "/usr/local/root/include/TProfile.h"
#include "/usr/local/root/include/TNtuple.h"
#include "/usr/local/root/include/TMapFile.h"



#define EQ_SCA 30
#define EQ_CR 60




/******************     FUNCTION PROTOTYPES     ****************/
int main (void);
void sethis (void);
void deftest (void);
void fillhis (void);
void histo_init (void);
void printError (char *where, int errorCode);
bool accettanza_test1(float , float );
bool accettanza_test2(float , float );
/***************************************************************/



// ====================================================================== //
// ====================================================================== //
// ====                                                              ==== //
// ====                    START OF MAIN PROGRAM                     ==== //
// ====                                                              ==== //
// ====================================================================== //
// ====================================================================== //



using namespace std;

int main () {

	
	
	//int 	npianiTST = 2;//modificato GIF
	int 	npianiTST = 4;
	int 	npianoTST = 0;
	
	//int 	nstripTST[npianiTST],neffTST[npianiTST],istripTST[npianiTST][24],numcluTST[npianiTST]; //modificato GIF
	int 	nstripTST[npianiTST],neffTST[npianiTST],istripTST[npianiTST][50],numcluTST[npianiTST];
	//clusizeTST[npianiTST][50]
	float	effTST[npianiTST];
	
	int 	npianiTRK = 4;
	int		npianoTRK = 0;
	
//	int 	nstripTRK[npianiTRK],neffTRK[npianiTRK],istripTRK[npianiTRK][100],clusizeTRK[npianiTRK][50],numcluTRK[npianiTRK];

	/*int neffcellstst1[50][50], neffcellstst2[50][50],nevcellstst1[50][50], nevcellstst2[50][50],
     	neffstrip_1X[50][50],neffstrip_1Y[50][50],neff_no_cut1[50][50],neffstrip_2X[50][50],neffstrip_2Y[50][50],neff_no_cut2[50][50],
	neff_no_cut1_xoy[50][50], neff_no_cut2_xoy[50][50];*/ //modificato GIF

 	int neffcellstst1[260][260], neffcellstst2[260][260],nevcellstst1[260][260], nevcellstst2[260][260],
     	neffstrip_1X[260][260],neffstrip_1Y[260][260],neff_no_cut1[260][260],neffstrip_2X[260][260],neffstrip_2Y[260][260],neff_no_cut2[260][260],
	neff_no_cut1_xoy[260][260], neff_no_cut2_xoy[260][260];

	
	
	//for (int i =0; i<= 50; i++) for (int j =0; j<= 50; j++) { //modificato GIF
	for (int i =0; i<= 259; i++) for (int j =0; j<= 259; j++) {
                           
		neffcellstst1[i][j] = 0; //numero di celle che sono state efficienti, modifiche GIF
		neffcellstst2[i][j] =0;
		nevcellstst1[i][j] = 0;
		nevcellstst2[i][j] =0;
		//nevcellstst1_all[i][j]=0;
		//nevcellstst2_all[i][j]=0;
		//nevcellstrk1[i][j]=0;
		//nevcellstrk2[i][j]=0;
		neffstrip_1X[i][j] = 0;
		neffstrip_1Y[i][j] = 0;
		neff_no_cut1[i][j]=0;
		neffstrip_2X[i][j] = 0;
		neffstrip_2Y[i][j] = 0;
		neff_no_cut2[i][j]=0;
		neff_no_cut1_xoy[i][j]=0;
		neff_no_cut2_xoy[i][j]=0;
	}
	
	
	int iimax, diff;
	double clusizeTST[npianiTST][50], clu, clu_tmp;
 
	for (int i = 0; i < npianiTST; i++){
		nstripTST[i] = 0;
		neffTST[i] = 0;
		numcluTST[i] = 0;
		
		for (int j = 0; j < 50; j++){ //modificato GIF, prima era j<50
			istripTST[i][j] = 0;
			clusizeTST[i][j] = 0;
		}
	}


//	float effTRK[npianiTRK];
	int nstripTRK[npianiTRK], neffTRK[npianiTRK], istripTRK[npianiTRK][96], numcluTRK[npianiTRK];
    	//neffcol[4][10], neffcolTRK[4][10];
		
	double clusizeTRK[npianiTRK][96];

	for (int i = 0; i < npianiTRK; i++){
		neffTRK[i] = 0;
		nstripTRK[i] = 0;
		numcluTRK[i] = 0;
		
		/*
		for (int j = 0; j < 10; j++){
			neffcol[i][j] = 0;
			neffcolTRK[i][j] = 0;
		}
		*/
		
		for (int j = 0; j < 96; j++){
			istripTRK[i][j] = 0;
			clusizeTRK[i][j] = 0.;
		}
	}
	



// per il tracking //

	//**************************************//
	//	TUTTE LE MISURE SONO ESPRESSE IN MM	//
	//**************************************//
	
	float x1, y1, x2, y2;		/* Coordinate in mm delle TRK 1 e 2 */
	float xtest1, ytest1, xtest2, ytest2;	/* Coordinate attese delle TST 1 e 2 */
	float xT1, yT1, xT2, yT2;	/* Coordinate misurate delle TST 1 e 2 */
	//int itest1, jtest1, itest2, jtest2;	/* istrip attesi delle TST 1 e 2 */
	int ncellsx,ncellsy;// numero di celle di cui si calcola l'efficienza
  
	float offsetX1 = 30.;		/* Offset della camera trk1 rispetto alla trk2 */
	float offsetY1 = 0.;		/* Offset della camera trk1 rispetto alla trk2 */
	float stripx1pitch = 21.25;	/* Strip LUNGHE trk1 (sopra) */
	float stripy1pitch = 22.8;	/* Strip CORTE  trk1 (sopra) */
	float stripx2pitch = 21.25;	/* Strip LUNGHE trk2 (sotto) */
	float stripy2pitch = 22.8;	/* Strip CORTE  trk2 (sotto) */
	float quotatrk1 = 2250.;	/* Quota camera trk1 (sopra) */
	float quotatrk2 = 420.;	/* Quota camera trk2 (sotto) */ 
	float posizione1 = 1660.;	/* Quota posizione 1 (sopra) */ //da modificare GIF
	//float posizione2 = 1320.;	/* Quota posizione 2  */ //da modificare GIF
	float posizione2 = 1400.;	/* Quota posizione 2 GIF  */ //modificato GIF
	float posizione3 = 970.;	/* Quota posizione 3  */ //da modificare GIF
	float posizione4 = 660.;	/* Quota posizione 4 (sotto) */ //da modificare GIF
	float quotatest1, quotatest2;
	float latox, latoy, lato1x, lato1y, lato2x, lato2y, Xcamera = 1641.6, Ycamera =850.; // lati delle celle e lati delle camere di tracking

	/***** Offset possibili delle TST 1 e 2 *****/
	float xoffT1[] = { 800, 0., 0., 0. }; //da modificare GIF
	float yoffT1[] = { 135.2, 0., 0., 0. }; //da modificare GIF
	float xoffT2[] = { 177.5, 0., 0., 0. };
	float yoffT2[] = { 22.81, 0., 0., 0. };
  
  

	/***** Passi delle camere TST 1 e 2 *****/
	float xpitch1;	/* Strip LUNGHE tst1 (sopra) */
	float ypitch1;	/* Strip CORTE  tst1 (sopra) */
	float xpitch2;	/* Strip LUNGHE tst2 (sotto) */
	float ypitch2;	/* Strip CORTE  tst2 (sotto) */
	/*
	float xp11 = 21.250, yp11 = 21.250, xp12 = 21.475, yp12 = 21.475;	 tipo 11=21.250 , 12=21.475 da modificare GIF
	float xp21 = 22.575, yp21 = 22.575, xp22 = 22.800, yp22 = 22.800;	 tipo	21=22.575 , 22=22.800 
	*/
	float xp11 = 21.2, yp11 = 21.2, xp12 = 21.2, yp12 = 21.2;	/* tipo 11=21.250 , 12=21.475 */ //modificato GIF
	float xp21 = 21.2, yp21 = 21.2, xp22 = 21.2, yp22 = 21.2;	/* tipo	21=22.575 , 22=22.800 */
	


	float distT2x, distT2y;
	float distT1x, distT1y;
	//int jollyFlag = 0, maxI = 0, maxJ = 0;



	// Rendimenti vari //
	int numcluOK, trackingOK, npianoOK;
	//int nevncol = 0;
	int nevnumclu = 0;
	int nevtracked = 0;
	int AnalyzedEvent = 0;
	int nevpianoOK =0;





	int		nwordcr = 0;
	int		nw = 0;
	int		one = 1;
	//int		clu, clu_tmp, iimax, diff;
	int		test;
	int		word;
	
	Float_t cameraineff1 = 0.;
	Float_t cameraineff2 = 0.;


	int		numEvFreq = 1000;			//	frequenza di printout
	int		numEv;
	
	int check = 0;
	int firstRun = 0;			// primo run da analizzare
	int lastRun = 0;			// ultimo run da analizzare
	int numRun = 0;				// run in analisi
	int Nrun = 1;				// numero totale di run da analizzare
	
	char strhisto[60];
	char strout[60];
	char strouteff[60];
	
	
	//int		nTRK1x=0, nTRK1y=0, nTRK1=0, nTRK2x=0, nTRK2y=0, nTRK2=0, nTST1x=0, nTST1y=0, nTST1=0, nTST2x=0, nTST2y=0, nTST2=0;
	
	cout << showbase 			// show the 0x prefix
         << internal 			// fill between the prefix and the number
         << setfill('0'); 		// fill with 0s



	do{	printf ("\nEnter first-run number\n");
		scanf ("%d", &firstRun);


		printf ("\nEnter last-run number\n");
		scanf ("%d", &lastRun);
		Nrun = lastRun - firstRun + 1;
		
		if (!(Nrun > 0)){
			printf ("\nERROR: invalid run numbers!\n");
			printf ("Please specify correct values\n\n");
			check = 0;
			continue;
		}
	
	check = 1;
	
	}	while (!check);

	
	sprintf (strout, USER_OUTFILE, firstRun);
	sprintf (strouteff, USER_EFFFILE, firstRun);
	sprintf (strhisto, USER_ROOTFILE, firstRun);



	int pos1,pos2;
        
	printf ("Posizione test1: (1 in alto,2,3,4 in basso)");
	scanf ("%d", &pos1);
	printf ("Posizione test2: (1 in alto,2,3,4 in basso)");
	scanf ("%d", &pos2);
        
	switch (pos1){
		case 1:
			quotatest1 = posizione1;
			break;

		case 2:
			quotatest1 = posizione2;
			break;

		case 3:
			quotatest1 = posizione3;
			break;

		case 4:
			quotatest1 = posizione4;
			break;
	}

	switch (pos2){
		case 1:
			quotatest2 = posizione1;
			break;

		case 2:
			quotatest2 = posizione2;
			break;

		case 3:
			quotatest2 = posizione3;
			break;

		case 4:
			quotatest2 = posizione4;
			break;
	}
	
	
	int ptest1,ptest2;
        
	printf ("Piano Test1 (11, 12, 21 o 22):");
	scanf ("%d", &ptest1);
	printf ("Piano Test2 (11, 12, 21 o 22)");
	scanf ("%d", &ptest2);
        
	switch (ptest1){
		case 11:
			xpitch1 = xp11;
			ypitch1 = yp11;
			break;

		case 12:
			xpitch1 = xp12;
			ypitch1 = yp12;
			break;

		case 21:
			xpitch1 = xp21;
			ypitch1 = yp21;
			break;

		case 22:
			xpitch1 = xp22;
			ypitch1 = yp22;;
			break;
	}

	switch (ptest2){
		case 11:
			xpitch2 = xp11;
			ypitch2 = yp11;
			break;

		case 12:
			xpitch2 = xp12;
			ypitch2 = yp12;
			break;

		case 21:
			xpitch2 = xp21;
			ypitch2 = yp21;
			break;

		case 22:
			xpitch2 = xp22;
			ypitch2 = yp22;;
			break;
	}
	
	float tested_range1x = ypitch1 * 24; //modificato per test GIF
	float tested_range1y = xpitch1 * 24; //modificato per test GIF
	//float tested_range1x = ypitch1 * 56; 
	//float tested_range1y = xpitch1 * 32;
	float tested_range2x = ypitch2 * 24; //modificato per test GIF (non viene analizzato)
	float tested_range2y = xpitch2 * 24; //modificato per test GIF (non viene analizzato)
	//float tested_range2x = ypitch2 * 56;
	//float tested_range2y = xpitch2 * 32;
	
				
	Float_t lambda1 = (quotatrk1 - quotatest1) / (quotatrk1 - quotatrk2);
	Float_t lambda2 = (quotatrk1 - quotatest2) / (quotatrk1 - quotatrk2);
	
	//printf("\n ho calcolato lambda1 = %f. lambda2 = %f\n", lambda1,lambda2);
	
	printf("Numero celle sull'asse x (strip Y): ");
	scanf ("%d", &ncellsx);
	printf("Numero celle sull'asse y (strip X): ");
	scanf ("%d", &ncellsy);
	
	latox = Xcamera / ncellsx;
	latoy = Ycamera / ncellsy;
	lato1x = tested_range1x / ncellsx;
	lato2x = tested_range2x / ncellsx;
	lato1y = tested_range1y / ncellsy;
	lato2y = tested_range2y / ncellsy;
       
	// printf("\ndopo i vari lati  lambda1 = %f. lambda2 = %f\n", lambda1,lambda2);
       
	printf("Lati celle sull'asse x (strip Y): \ntest1x: %f, test2x: %f\n",lato1x,lato2x);
	printf("Lati celle sull'asse y (strip X): \ntest1y: %f, test2y: %f\n",lato1y,lato2y);
	//  printf("\nora lambda1 = %f. lambda2 = %f\n", lambda1,lambda2);
	int calcoloeff;
	//  printf("\nora ho dichiarato c.e.: lambda1 = %f. lambda2 = %f\n", lambda1,lambda2);
	printf ("Prova: Run di calcolo efficienza(1) o di calcolo offset?(0):");
		      
	scanf ("%d", &calcoloeff);
	
	if(calcoloeff ==0) {	// azzero gli offset prima di far partire un run di calcolo offset
		xoffT1[0]=0.;
		xoffT2[0]=0.;
		yoffT1[0]=0.;
		yoffT2[0]=0.;
	}
	
	
	
	
	
	
	////////////  Opening output files  ////////////////
	
	FILE *fout;
	FILE *fouteff;
	TFile *f;

	if ((f = new TFile (strhisto, "RECREATE")) == NULL){			// ROOT file
		printf ("\nERROR: Cant'open file \"%s\"\n\n", strhisto);
		exit (1);
	}

	if ((fouteff = fopen (strouteff, "w+")) == NULL){				// EFF file
		printf ("\nERROR: Cant'open file \"%s\"\n\n", strouteff);
		exit (1);
	}

	if ((fout = fopen (strout, "w+")) == NULL){						// printf
		printf ("\nERROR: Cant'open file \"%s\"\n\n", strout);
		exit (1);
	}

	
	
	
	
	
	
	/*
	char RunNumber[99];
	cout << "Enter run number: ";
	cin >> RunNumber;
	char file_name[99];
	sprintf(file_name, "%s.bin", RunNumber);
	*/
	
	

	
	
	/*
	char root_file_name[99];
	sprintf(root_file_name, "%s_analysis.root", RunNumber);
	//sprintf (strhisto, USER_ROOTFILE, runrepl);
	//Create a root file for the histo
	TFile *f= new TFile(root_file_name,"RECREATE");
	*/

	


	//system("cp hist_rpc.las hist_standard.las");
	system (HIST_ANAL_TO_HIST_STANDARD);
	printf("Reading histogram definitions\n");
	histo_init();
	printf("After histo_init\n");
	
		
	int eq_id=0;
	int event[19];
	int Rscalers[357];
	int *p;
	
	cout<<"dimensione eq_id = "<<sizeof(eq_id)<<endl;
	
	
	


	/************************************************************/
	/************************************************************/


for (int iii = firstRun; iii < (firstRun + Nrun); iii++){
	

	//Open input file with data
	char file_name[99];
	numRun = iii;
	sprintf(file_name, "%03d.bin", numRun);
	ifstream infile (file_name, ios::binary);
	
	
	fprintf(fout, "*******************************\n");
	fprintf(fout, "**                           **\n");
	fprintf(fout, "**     INIZIO RUN n. %03d     **\n", numRun);
	fprintf(fout, "**                           **\n");
	fprintf(fout, "*******************************\n");
	
	
	
	while(infile.read ((char*)&eq_id, sizeof(eq_id))){
		
		printf("reading bin file\n");
		npianoTST = 0;
		npianoTRK = 0;
		
		nwordcr = 0;
		
		
		
		for (int i=0; i<npianiTST; i++){
			nstripTST[i] = 0;
			numcluTST[i] = 0;
			
			//for (int j=0; j<24; j++){ //modificato GIF
			for (int j=0; j<50; j++){
				istripTST[i][j] = 0;
				clusizeTST[i][j] = 0;
			}
		}
	
	
		for (int i=0; i<npianiTRK; i++){
			nstripTRK[i] = 0;
			numcluTRK[i] = 0;
			
			for (int j=0; j<96; j++){
				istripTRK[i][j] = 0;
				clusizeTRK[i][j] = 0;
			}
		}
	
		
		
		
		
		
		
		
		
		
		
		
		
		//--------------------------------------------------------------------------------------------------//
		//**************************************************************************************************//
		//																									//
		//									INIZIO LETTURA													//
		//																									//
		//**************************************************************************************************//
		//--------------------------------------------------------------------------------------------------//
		
		
		//	*******************************	SCALERS	***********************************	//
		
		if (eq_id == EQ_SCA){
		
			cout<<endl<<"LETTURA SCALERS..."<<endl;
			fprintf(fout, "\n\nLETTURA SCALERS...\n");
		
			infile.seekg(-4, ios::cur);
	
			for (int i=0; i<357; i++){
				Rscalers[i]=0;
			}

			infile.read ((char*)&Rscalers, sizeof(Rscalers));
			
			p = Rscalers;
			
			cout<<"eq_id  = "<<dec<<*p<<endl;
			fprintf(fout, "Eq_ID = %d\n", *p);
			
			p++;
			cout<<"numEv  = "<<dec<<*p<<endl;
			fprintf(fout, "numEv = %d\n", *p);
			
			p++;
			cout<<"TM     = "<<dec<<*p<<endl;
			fprintf(fout, "TM = %d\n", *p);
			
			p++;
			cout<<"T1     = "<<dec<<*p<<endl;
			fprintf(fout, "T1 = %d\n", *p);
			
			p++;
			cout<<"T2     = "<<dec<<*p<<endl;
			fprintf(fout, "T2 = %d\n", *p);
			
			p++;

			
			for (int i=0; i<352; i++){
			 //da modificare
				if(i<32){
					cout<<"TST1x ch. "<<i<<": "<<dec<<*p<<endl;
					fprintf(fout, "TST1x ch. %d: %d\n", i, *p);
					p++;
				}
				else if(i>31 && i<64){
					cout<<"TST1y ch. "<<i-32<<": "<<dec<<*p<<endl;
					fprintf(fout, "TST1y ch. %d: %d\n", i-32, *p);
					p++;
				}
				else if(i>63 && i<96){
					cout<<"TST2x ch. "<<i-64<<": "<<dec<<*p<<endl;
					fprintf(fout, "TST2x ch. %d: %d\n", i-64, *p);
					p++;
				}
				else if(i>95 && i<128){
					cout<<"TST2y ch. "<<i-96<<": "<<dec<<*p<<endl;
					fprintf(fout, "TST2y ch. %d: %d\n", i-96, *p);
					p++;
				}

				else if(i>127 && i<168){
					cout<<"TRK1x ch. "<<i-128<<": "<<dec<<*p<<endl;
					fprintf(fout, "TRK1x ch. %d: %d\n", i-128, *p);
					p++;
				}
				else if(i>167 && i<240){
					cout<<"TRK1y ch. "<<i-168<<": "<<dec<<*p<<endl;
					fprintf(fout, "TRK1y ch. %d: %d\n", i-168, *p);
					p++;
				}
				else if(i>239 && i<280){
					cout<<"TRK2x ch. "<<i-240<<": "<<dec<<*p<<endl;
					fprintf(fout, "TRK2x ch. %d: %d\n", i-240, *p);
					p++;
				}
				else if(i>279 && i<352){
					cout<<"TRK2y ch. "<<i-280<<": "<<dec<<*p<<endl;
					fprintf(fout, "TRK2y ch. %d: %d\n", i-280, *p);
					p++;
				}

			}		//	chiusura ciclo for sugli scaler
			

			cout<<"FINE LETTURA SCALERS"<<endl<<endl;
			fprintf(fout, "FINE LETTURA SCALERS...\n\n");

	
		}	//	chiusura if eq_id=60
				
		
		
		
		
		
		
		//	*******************************	CR	***********************************	//

	
		else if (eq_id == EQ_CR){
		
			fprintf(fout, "\n\nLETTURA CR...\n");


			infile.seekg(-4, ios::cur);
			
			for (int i=0; i<19; i++){
				event[i]=0;
			}
		
			infile.read ((char*)&event, sizeof(event));
		
			p = event;
	
			//cout<<"eq_id  = "<<dec<<*p<<endl;
			fprintf(fout, "Eq_ID = %d\n", *p);
			p++;
;
			numEv=*p;
			if(numEv%numEvFreq==0)cout<<"numEv  = "<<dec<<*p<<endl;
			fprintf(fout, "numEv = %d\n", *p);
			
			p++;
			if(numEv%numEvFreq==0)cout<<"TM     = "<<dec<<*p<<endl;
			fprintf(fout, "TM = %d\n", *p);

			p++;
			if(numEv%numEvFreq==0)cout<<"T1     = "<<dec<<*p<<endl;
			fprintf(fout, "T1 = %d\n", *p);

			p++;
			if(numEv%numEvFreq==0)cout<<"T2     = "<<dec<<*p<<endl;
			fprintf(fout, "T2 = %d\n", *p);
			
			
			if(numEv%numEvFreq==0)cout<<endl<<"LETTURA CAMERE DI TEST..."<<endl;
			fprintf(fout, "\nLETTURA CAMERE DI TEST...\n");
			

			nw=4;
			
			for(int i=0; i<nw; i++){
			
			
				p++;
				word = *p;
				if(numEv%numEvFreq==0)cout<<dec<<i<<") word  = "<<hex<<word<<endl;
				fprintf(fout, "word = %08X\n", word);
				cout << "word: " << word << endl;

				
				for(int j=0; j<32; j++){ //Original version
				
					test=one<<j;
					//cout<<"test  = "<<hex<<test<<endl;
					
					//cout << "npianoTST before: " << npianoTST << " nwordcr: " << nwordcr << endl; //debug
				
					
					if((word & test) != 0){
	
						//cout<<"test  = "<<hex<<test<<endl;
						
						nstripTST[npianoTST]++;
						
						switch (npianoTST){
				
							case 0:			// TST2y
				  				istripTST[npianoTST][nstripTST[npianoTST]] = nwordcr + 1;
								//cout << "case 0, npianoTST: " << npianoTST << " nstripTST[npianoTST]:" << nstripTST[npianoTST] << " strip: " << nwordcr + 1 << endl;
				  				break;

							case 1:			// TST2x
								//istripTST[npianoTST][nstripTST[npianoTST]] = nwordcr + 1 - 32;
								istripTST[npianoTST][nstripTST[npianoTST]] = nwordcr + 1 - 24; //modificato GIF
								//cout << "case 1, npianoTST: " << npianoTST << " nstripTST[npianoTST]:" << nstripTST[npianoTST] << " strip: "
								//<< nwordcr + 1 - 24 << endl;
								break;

							case 2:			// TST1y
								istripTST[npianoTST][nstripTST[npianoTST]] = nwordcr + 1 - 64; // 
								//cout << "case 2, npianoTST: " << npianoTST << " nstripTST[npianoTST]:" << nstripTST[npianoTST] << " strip: "
								//<< nwordcr + 1 -64 << endl;
								//istripTST[npianoTST][nstripTST[npianoTST]] = nwordcr + 1 - 56; //modificato GIF 
								break;

							case 3:			// TST1x
								istripTST[npianoTST][nstripTST[npianoTST]] = nwordcr + 1 - 96;
								//cout << "case 3, npianoTST: " << npianoTST << " nstripTST[npianoTST]:" << nstripTST[npianoTST] << " strip: "
								//<< nwordcr + 1 - 96 << endl;
								//istripTST[npianoTST][nstripTST[npianoTST]] = nwordcr + 1 - 88; //modificato GIF
								break;
				  
						}	//	chiusura switch
						
						
					
					}	//	 chiusura if word==test
					
					//31 -> 63 -> 95 -> 127 original
					//31 -> 63 -> 87 -> 111 ours
					
					//if (nwordcr == 31 || nwordcr == 63 || nwordcr == 95 || nwordcr == 127){
					//if (nwordcr == 31 || nwordcr == 63 || nwordcr == 87 || nwordcr == 111){ //modificato GIF
			        	//npianoTST++;
					//}
					
					if (nwordcr == 23 || nwordcr == 63 || nwordcr == 95 || nwordcr == 127) {
					npianoTST++;
					}
					
					
					nwordcr++;
				
				}	//	chiusura ciclo for sui 32 bit
			
			
			
			}	//	chiusura sul numero di parole per le camere di test
			
			//Se abbiamo capito -> npianoTST = 2 -> strip perpendicolari al muro
			//npianoTST3 -> Stip parallele al muro
			
			cout << "nstripTST[0]: " << nstripTST[0] << endl;
			for (int i = 0; i < nstripTST[0]; i++) {
			cout << istripTST[0][i] << endl;
			}
			
			/*for (int i = 0; i < nstripTST[1]; i++) {
				if (istripTST[1][i] == 1) {istripTST[1][i] = 8;}
				else if (istripTST[1][i] == 2) {istripTST[1][i] = 7;}
				else if (istripTST[1][i] == 3) {istripTST[1][i] = 6;}
				else if (istripTST[1][i] == 4) {istripTST[1][i] = 5;}
				else if (istripTST[1][i] == 5) {istripTST[1][i] = 4;}
				else if (istripTST[1][i] == 6) {istripTST[1][i] = 3;}
				else if (istripTST[1][i] == 7) {istripTST[1][i] = 2;}
				else if (istripTST[1][i] == 8) {istripTST[1][i] = 1;}
		
				else if (istripTST[1][i] == 9) {istripTST[1][i] = 16;}
				else if (istripTST[1][i] == 10) {istripTST[1][i] = 15;}
				else if (istripTST[1][i] == 11) {istripTST[1][i] = 14;}
				else if (istripTST[1][i] == 12) {istripTST[1][i] = 13;}
				else if (istripTST[1][i] == 13) {istripTST[1][i] = 12;}
				else if (istripTST[1][i] == 14) {istripTST[1][i] = 11;}
				else if (istripTST[1][i] == 15) {istripTST[1][i] = 10;}
				else if (istripTST[1][i] == 16) {istripTST[1][i] = 9;}
				
				else if (istripTST[1][i] == 17) {istripTST[1][i] = 24;}
				else if (istripTST[1][i] == 18) {istripTST[1][i] = 23;}
				else if (istripTST[1][i] == 19) {istripTST[1][i] = 22;}
				else if (istripTST[1][i] == 20) {istripTST[1][i] = 21;}
				else if (istripTST[1][i] == 21) {istripTST[1][i] = 20;}
				else if (istripTST[1][i] == 22) {istripTST[1][i] = 19;}
				else if (istripTST[1][i] == 23) {istripTST[1][i] = 18;}
				else if (istripTST[1][i] == 24) {istripTST[1][i] = 17;}
				
				//cout << "strips invertite istripTST[0][i]" << istripTST[0][i] << endl;
			}/*
			
			
			
			for (int i=0; i<npianiTST; i++){
			
				fprintf(fout, "Numero di strip colpite nel piano %d = %d\n", i, nstripTST[i]);
				
				for (int j=1; j<nstripTST[i]+1; j++){
					fprintf(fout, "%d) %d\n", j, istripTST[i][j]);
				}
				
			}

			
			if(numEv%numEvFreq==0){
		
				for (int i=0; i<npianiTST; i++){
					cout<<"numero di strip colpite nel piano "<<dec<<i<<" = "<<nstripTST[i]<<endl;
					//neffTST[i] = 0;
					//numcluTST[i] = 0;
					for (int j=1; j<nstripTST[i]+1; j++){
						cout<<dec<<j<<") "<<istripTST[i][j]<<endl;
					}
					//for (int j=0; j<50; j++){
						//clusizeTST[i][j] = 0;
					//}
				}
	
			}
		
						
			
			for(npianoTST=0; npianoTST<npianiTST; npianoTST++){
			
				if(nstripTST[npianoTST] > 0){
					neffTST[npianoTST] = neffTST[npianoTST] + 1;		// calcolo l'efficienza delle camere di TEST
				}
				
				if(numEv%numEvFreq==0){
					printf("neffTST[%d] = %d \n", npianoTST, neffTST[npianoTST]);
					fprintf(fout, "neffTST[%d] = %d \n", npianoTST, neffTST[npianoTST]);
				}
				
				var.hisvar[npianoTST*100 + TSTstripOffset] = (float) nstripTST[npianoTST];
				
				if(numEv%numEvFreq==0){
					printf("NUM STRIP var.hisvar[%d] = %f \n",npianoTST*100 + TSTstripOffset, var.hisvar[npianoTST*100 + TSTstripOffset]);
					fprintf(fout, "NUM STRIP var.hisvar[%d] = %f \n",npianoTST*100 + TSTstripOffset, var.hisvar[npianoTST*100 + TSTstripOffset]);
				}
				
				for(int j=1; j<nstripTST[npianoTST]+1; j++){
					var.hisvar[npianoTST*100 + j + TSTstripOffset] = (float) istripTST[npianoTST][j];
					if(numEv%numEvFreq==0){
						printf("j=%d \n",j);
						fprintf(fout, "j=%d \n",j);
						printf("STRIP COLPITE var.hisvar[%d] = %f \n",npianoTST*100 + j + TSTstripOffset, var.hisvar[npianoTST*100 + j + TSTstripOffset]);
						fprintf(fout, "STRIP COLPITE var.hisvar[%d] = %f \n",npianoTST*100 + j + TSTstripOffset, var.hisvar[npianoTST*100 + j + TSTstripOffset]);
					}
				}
				
				if(numEv%numEvFreq==0){
					printf("MOLTEPLICITA' var.hisvar[%d] = %d \n",npianoTST + TSTmulOffset, nstripTST[npianoTST]);
					fprintf(fout, "MOLTEPLICITA' var.hisvar[%d] = %d \n",npianoTST + TSTmulOffset, nstripTST[npianoTST]);
				}
				
				var.hisvar[npianoTST + TSTmulOffset] = (float) nstripTST[npianoTST];
      
	  
	  
	  
				//-------CALCOLO LA CLUSTER SIZE------------//
      
				for(int j=1; j<=50; j++){
					clusizeTST[npianoTST][j]=0;		// pulizia contatore
				}
				
				
				numcluTST[npianoTST]=0;
				clu=0.;
				clu_tmp=0.;
				
				if(nstripTST[npianoTST]>=1){		// richiedo che ci sia almeno una strip colpita
				
					//printf("inizio \n");
					clu = 1.;
					clu_tmp = 1.;
					numcluTST[npianoTST] = 1;			// 1 cluster
					clusizeTST[npianoTST][1] = 1.;		// di dimensione 1
	
					if(nstripTST[npianoTST]>1){			// se c'e' piu' di una strip colpita
					
						iimax = nstripTST[npianoTST] - 1;
						
						for(int ii=1; ii<=iimax; ii++){
						
							diff = istripTST[npianoTST][ii+1] - istripTST[npianoTST][ii];
							
							if(diff==1.){		// controllo che le strip siano adiacenti
							
								clu = clu + 1.;
								
								if((ii==(nstripTST[npianoTST]-1)) && (clu>clu_tmp)){
									clu_tmp = clu;
								}
							}
							
							if((diff>1) || (ii==(nstripTST[npianoTST]-1))){		// se non sono adiacenti o se ho finito le strip colpite da controllare
							
								clusizeTST[npianoTST][numcluTST[npianoTST]] = clu;		// allora chiudo il cluster, con dimensione clu
								
		  						if(ii != (nstripTST[npianoTST]-1)){				// se non ho ancora finito le strip colpite da controllare
											
									numcluTST[npianoTST] = numcluTST[npianoTST] + 1;	// allora apro un altro cluster
								}
								
								if((diff>1) && (ii==(nstripTST[npianoTST]-1))){	// se non sono adiacenti e ho finito le strip colpite da controllare
								
									numcluTST[npianoTST] = numcluTST[npianoTST] + 1;	// allora apro un ultimo cluster
									clusizeTST[npianoTST][numcluTST[npianoTST]] = 1;	// e gli do dimensione 1
		      
								}
								
								if(clu>clu_tmp){
									clu_tmp = clu;
								}
								
								clu=1.;		// avendo aperto un nuovo cluster, riazzero la dimensione
							}
						}
					}
					
					//printf("fine \n");

				}
	
	
	
				var.hisvar[npianoTST*25 + cluTSTOffset] = (float) numcluTST[npianoTST];	            
				
				if(numcluTST[npianoTST]>0){
				
					for(int j=1; j<=numcluTST[npianoTST]; j++){
    
						if(numEv%numEvFreq==0){
							printf("CLUSTER SIZE var.hisvar[%d] = %f \n",npianoTST*25 + j + cluTSTOffset, clusizeTST[npianoTST][j]);
							fprintf(fout, "CLUSTER SIZE var.hisvar[%d] = %f \n",npianoTST*25 + j + cluTSTOffset, clusizeTST[npianoTST][j]);
						}
						
						var.hisvar[npianoTST*25 + j + cluTSTOffset] = (float) clusizeTST[npianoTST][j];
					}
				}
				
				if(numEv%numEvFreq==0){
					printf("NUM CLUSTER var.hisvar[%d] = %d \n", npianoTST + numcluTSTOffset, numcluTST[npianoTST]);
					fprintf(fout, "NUM CLUSTER var.hisvar[%d] = %d \n", npianoTST + numcluTSTOffset, numcluTST[npianoTST]);
				}
				
				var.hisvar[npianoTST + numcluTSTOffset] = (float) numcluTST[npianoTST];
  
  
	
				
			}	// chiusura ciclo for sul numero di piani
			
			

		
			/*	
			
			if (numcluTST[0] > 0) nTST1x++;
			if (numcluTST[1] > 0) nTST1y++;
			if (numcluTST[0] > 0 && numcluTST[1] > 0) nTST1++;   
    
				
			if (numcluTST[2] > 0) nTST2x++;
			if (numcluTST[3] > 0) nTST2y++;
			if (numcluTST[2] > 0 && numcluTST[3] > 0) nTST2++;   	
			
			*/
	
	
	
	
	
	
	//-------------------------------------------------------------------------------------------------------
		
		
		
			if(numEv%numEvFreq==0)cout<<"LETTURA CAMERE DI TRACKING..."<<endl;
			fprintf(fout, "\nLETTURA CAMERE DI TRACKING...\n");


			nw=10;
			
			for(int i=0; i<nw; i++){
			
			
				p++;
				word = *p;
				if(numEv%numEvFreq==0)cout<<dec<<i<<") word  = "<<hex<<word<<endl;
				fprintf(fout, "word = %08X\n", word);

				for(int j=0; j<32; j++){
				
					test=one<<j;
					//cout<<"test  = "<<hex<<test<<endl;
				
					
					if((word & test) != 0){
						
						nstripTRK[npianoTRK]++;
												
						switch (npianoTRK){
				
							case 0:			// TRK2y
				  				istripTRK[npianoTRK][nstripTRK[npianoTRK]] = nwordcr + 1 - 128;
				  				break;

							case 1:			// TRK2x
								istripTRK[npianoTRK][nstripTRK[npianoTRK]] = nwordcr + 1 - 128 - 96;
								break;

							case 2:			// TRK1y
								istripTRK[npianoTRK][nstripTRK[npianoTRK]] = nwordcr + 1 - 128 - 96 - 64;
								break;

							case 3:			// TRK1x
								istripTRK[npianoTRK][nstripTRK[npianoTRK]] = nwordcr + 1 - 128 - 96 - 64 - 96;
								break;
				  
						}	//	chiusura switch
					
					}	//	 chiusura if word==test
					
					
					//if (nwordcr == 191 || nwordcr == 287 || nwordcr == 351 || nwordcr == 447){
			        if (nwordcr == 223 || nwordcr == 287 || nwordcr == 383 || nwordcr == 447){
			        	npianoTRK++;
					}
					
					nwordcr++;
				
				}	//	chiusura ciclo for sui 32 bit
			
			
			}	//	chiusura sul numero di parole per le camere di tracking
			

			
			
			for (int i=0; i<npianiTRK; i++){
			
				fprintf(fout, "Numero di strip colpite nel piano %d = %d\n", i, nstripTRK[i]);
				
				for (int j=1; j<nstripTRK[i]+1; j++){
					fprintf(fout, "%d) %d\n", j, istripTRK[i][j]);
				}
				
			}
			


						
			if(numEv%numEvFreq==0){
			
				for (int i=0; i<npianiTRK; i++){
					cout<<"numero di strip colpite nel piano "<<dec<<i<<" = "<<nstripTRK[i]<<endl;
					//neffTRK[i] = 0;
					//numcluTRK[i] = 0;
					for (int j=1; j<nstripTRK[i]+1; j++){
						cout<<dec<<j<<") "<<istripTRK[i][j]<<endl;
					}
					//for (int j=1; j<numcluTRK[i]+1; j++){
						//clusizeTRK[i][j] = 0;
					//}
				}
			
			}
			
			
			
			trackingOK = numcluOK = npianoOK = 0;
			
			for(npianoTRK=0; npianoTRK<4; npianoTRK++){
			
				if(nstripTRK[npianoTRK] > 0){
					neffTRK[npianoTRK] = neffTRK[npianoTRK] + 1;		// calcolo l'efficienza delle camere di Tracking
			
				}
				
				if(numEv%numEvFreq==0){
					printf("nefftrk[%d] = %d \n", npianoTRK, neffTRK[npianoTRK]);
					fprintf(fout, "nefftrk[%d] = %d \n", npianoTRK, neffTRK[npianoTRK]);
				}
				
				var.hisvar[npianoTRK*100 + TRKstripOffset] = (float) nstripTRK[npianoTRK];
				
				if(numEv%numEvFreq==0){
					printf("NUM STRIP var.hisvar[%d] = %f \n",npianoTRK*100 + TRKstripOffset, var.hisvar[npianoTRK*100 + TRKstripOffset]);
					fprintf(fout, "NUM STRIP var.hisvar[%d] = %f \n",npianoTRK*100 + TRKstripOffset, var.hisvar[npianoTRK*100 + TRKstripOffset]);
				}
				
				for(int j=1; j<nstripTRK[npianoTRK]+1; j++){
					var.hisvar[npianoTRK*100 + j + TRKstripOffset] = (float) istripTRK[npianoTRK][j];
					if(numEv%numEvFreq==0){
						printf("j=%d \n",j);
						printf("STRIP COLPITE var.hisvar[%d] = %f \n",npianoTRK*100 + j + TRKstripOffset, var.hisvar[npianoTRK*100 + j + TRKstripOffset]);
						fprintf(fout, "j=%d \n",j);
						fprintf(fout, "STRIP COLPITE var.hisvar[%d] = %f \n",npianoTRK*100 + j + TRKstripOffset, var.hisvar[npianoTRK*100 + j + TRKstripOffset]);
					}
					
				}
				
				if(numEv%numEvFreq==0){
					printf("MOLTEPLICITA' var.hisvar[%d] = %d \n",npianoTRK + TRKmulOffset, nstripTRK[npianoTRK]);
					fprintf(fout, "MOLTEPLICITA' var.hisvar[%d] = %d \n",npianoTRK + TRKmulOffset, nstripTRK[npianoTRK]);
				}
				
				var.hisvar[npianoTRK + TRKmulOffset] = (float) nstripTRK[npianoTRK];
      
	  
	  
	  
				//-------CALCOLO LA CLUSTER SIZE------------//
      
				for(int j=1; j<=96; j++){
					clusizeTRK[npianoTRK][j]=0;		// pulizia contatore
				}
				
				
				numcluTRK[npianoTRK]=0;
				clu=0.;
				clu_tmp=0.;
				
				if(nstripTRK[npianoTRK]>=1){
				
					//printf("inizio \n");
					clu = 1.;
					clu_tmp = 1.;
					numcluTRK[npianoTRK] = 1;
					clusizeTRK[npianoTRK][1] = 1.;
	
					if(nstripTRK[npianoTRK]>1){
					
						iimax = nstripTRK[npianoTRK] - 1;
						
						for(int ii=1; ii<=iimax; ii++){
						
							diff = istripTRK[npianoTRK][ii+1] - istripTRK[npianoTRK][ii];

							if(diff==1.){
							
								clu = clu + 1.;
								
								if((ii==(nstripTRK[npianoTRK]-1))&&(clu>clu_tmp)){
									clu_tmp = clu;
								}
							}
							
							if((diff>1)||(ii==(nstripTRK[npianoTRK]-1))){
							
								clusizeTRK[npianoTRK][numcluTRK[npianoTRK]] = clu;
								
		  									if(ii!=(nstripTRK[npianoTRK]-1)){
											
									numcluTRK[npianoTRK] = numcluTRK[npianoTRK] + 1;
								}
								
								if((diff>1)&&(ii==(nstripTRK[npianoTRK]-1))){
								
									numcluTRK[npianoTRK] = numcluTRK[npianoTRK] + 1;
									clusizeTRK[npianoTRK][numcluTRK[npianoTRK]] = 1;
		      
								}
								
								if(clu>clu_tmp){
									clu_tmp = clu;
								}
								
								clu=1.;
							}
						}
					}
					
					//printf("fine \n");

				}
	
	
	
				var.hisvar[npianoTRK*50 + cluTRKOffset] = (float) numcluTRK[npianoTRK];	            
				
				if(numcluTRK[npianoTRK]>0){
				
					for(int j=1; j<=numcluTRK[npianoTRK]; j++){
    
						if(numEv%numEvFreq==0){
							printf("CLUSTER SIZE var.hisvar[%d] = %f \n",npianoTRK*50 + j + cluTRKOffset, clusizeTRK[npianoTRK][j]);
							fprintf(fout, "CLUSTER SIZE var.hisvar[%d] = %f \n",npianoTRK*50 + j + cluTRKOffset, clusizeTRK[npianoTRK][j]);
						}
						
						var.hisvar[npianoTRK*50 + j + cluTRKOffset] = (float) clusizeTRK[npianoTRK][j];
					}
				}
				
				if(numEv%numEvFreq==0){
					printf("NUM CLUSTER var.hisvar[%d] = %d \n", npianoTRK + numcluTRKOffset, numcluTRK[npianoTRK]);
					fprintf(fout, "NUM CLUSTER var.hisvar[%d] = %d \n", npianoTRK + numcluTRKOffset, numcluTRK[npianoTRK]);
				}
				
				var.hisvar[npianoTRK + numcluTRKOffset] = (float) numcluTRK[npianoTRK];
  
  				
				
				
				
				
				
				
				if (nstripTRK[npianoTRK] > 0){		// deve esserci almeno una strip colpita per piano
					++npianoOK;
					//printf("\nsto incrementando npianoOK; nwft vale %d\n", nwordferatrk);
					//++neffcol[npianoTRK][0];
		
					if (numcluTRK[npianoTRK] == 1){		// voglio che ci sia un solo cluster
						++numcluOK;
						//printf("\nsto incrementando numcluOK; nwft vale %d\n", nwordferatrk);

						if (nstripTRK[npianoTRK] < 3){		// e voglio che questo cluster non abbia piu' di 2 strip colpite
							//++neffcolTRK[npianoTRK][0];
							++trackingOK;
						}
					}
				}
	
	
	
	
				
			}	// chiusura ciclo for sul numero di piani
			
			
			
			
			/*
			
			if (numcluTRK[0] > 0) nTRK1x++;
			if (numcluTRK[1] > 0) nTRK1y++;
			if (numcluTRK[0] > 0 && numcluTRK[1] > 0) nTRK1++;   
    
			if (numcluTRK[2] > 0) nTRK2x++;
			if (numcluTRK[3] > 0) nTRK2y++;
			if (numcluTRK[2] > 0 && numcluTRK[3] > 0) nTRK2++;   
    	
			*/
	
	



			/************************************************
			**********          TRACKING           **********
			*************************************************
			Per il tracking uso come origine lo spigolo
			della camera inferiore (trk2) disegnato in figura;
			rispetto ad esso sono calcolati tutti gli offset.

			           MURO
			   XXX +++++++++++++++++++  C
			M  XXX                   +  R
			U  +                     +  A
			R  +      TOP VIEW       +  T
			O  +       (trk1)        +  E
			   +                     +  S
			   +++++++++++++++++++++++
			           STANZA


			Le variabili di offset sono definite
			e inizializzate all'inizio del programma

			************************************************* 
			      TUTTE LE MISURE SONO ESPRESSE IN MM
			*************************************************/




			x1 = y1 = x2 = y2 = -1000.;
			xtest1 = ytest1 = xtest2 = ytest2 = -5000.;
			xT1 = yT1 = xT2 = yT2 = 5000.;

	
			if (numcluOK == 4) ++nevnumclu;			// Calcolo dei rendimenti //
					
                          
			if (npianoOK == 4) ++nevpianoOK;
	     
            
			if (trackingOK == 4){
				
				++nevtracked;						// Calcolo dei rendimenti //

				/**  NB le strip_x (lunghe) forniscono la coordinata cartesiana y! **/
				y1 = stripx1pitch * (istripTRK[3][1] + nstripTRK[3] / 2. - 1.) + offsetY1;
				x1 = stripy1pitch * (istripTRK[2][1] + nstripTRK[2] / 2. - 1.) + offsetX1;
				y2 = stripx2pitch * (istripTRK[1][1] + nstripTRK[1] / 2. - 1.);
				x2 = stripy2pitch * (istripTRK[0][1] + nstripTRK[0] / 2. - 1.);
cout << x2 << " " << stripy2pitch << " " << istripTRK[0][1] << " " << nstripTRK[0] << endl;
		  
				//if(eventCount % 10000 == 0) printf("\nevento %d", eventCount);
		  
				//if(eventCount % 10000 == 0) printf("\ntrk1 : strips %d, %d, x1 = %f, y1 = %f", istriptrk[2][1] ,istriptrk[3][1], x1, y1);
				fprintf(fout, "\nTRK1 : strips %d, %d, x1 = %f, y1 = %f\n", istripTRK[2][1] ,istripTRK[3][1], x1, y1);
				//if(eventCount % 10000 == 0) printf("\ntrk2 : strips %d, %d, x2 = %f, y2 = %f", istriptrk[0][1] ,istriptrk[1][1], x2, y2);
				fprintf(fout, "\nTRK2 : strips %d, %d, x2 = %f, y2 = %f\n", istripTRK[0][1] ,istripTRK[1][1], x2, y2);
				
				// Coordinate attese 
				// printf("\nsto per usare lambda1 = %f, lambda2 = %f", lambda1,lambda2);
				xtest1 = x1 + lambda1 * (x2 - x1);
				ytest1 = y1 + lambda1 * (y2 - y1);
				xtest2 = x1 + lambda2 * (x2 - x1);
				ytest2 = y1 + lambda2 * (y2 - y1);
		  
				//fprintf(fout, "\nHo usato lambda1 = %f. lambda 2 = %f\n", lambda1,lambda2);
				fprintf(fout, "\nEvento %d: x1teo = %f, y1teo = %f, x2teo = %f, y2teo = %f\n", numEv, xtest1, ytest1, xtest2, ytest2);
				//if(eventCount % 10000 == 0) printf("\nevento %d: x1teo = %f, y1teo = %f, x2teo = %f, y2teo = %f",eventCount, xtest1, ytest1,xtest2,ytest2);
                  
                 
				if(calcoloeff){		// divisione in celle per il calcolo dell'efficienza
				
					for (int i = 1; i <= ncellsx; i++) for (int j = 1; j <= ncellsy; j++){
        
						if ((i-1)*lato1x + xoffT1[0]  <= xtest1 && xtest1 < i*lato1x + xoffT1[0] &&    
							(j-1)*lato1y + yoffT1[0]  <= ytest1 && ytest1 < j*lato1y+yoffT1[0]) {
								
								cameraineff1 = 1.;
								++nevcellstst1[i][j];
								if (nstripTST[0] > 0) ++neffstrip_1Y[i][j];
								if (nstripTST[1]> 0) ++neffstrip_1X[i][j];
								if (nstripTST[0] > 0 && nstripTST[1]> 0) ++neff_no_cut1[i][j];  //qui c'� un &...se mettessi ||?
								if (nstripTST[0] > 0 || nstripTST[1]> 0) ++neff_no_cut1_xoy[i][j];
						}
                   
						if ((i-1)*lato2x + xoffT2[0] <= xtest2 && xtest2 < i*lato2x + xoffT2[0]  &&
							(j-1)*lato2y + yoffT2[0] <= ytest2 && ytest2 < j*lato2y + yoffT2[0]) {
								
								cameraineff2 = 1.;
								++nevcellstst2[i][j];                         
								if (nstripTST[2] > 0) ++neffstrip_2Y[i][j];
								if (nstripTST[3] > 0) ++neffstrip_2X[i][j];
								if (nstripTST[2] > 0 && nstripTST[3] > 0) ++neff_no_cut2[i][j];
								if (nstripTST[2] > 0 || nstripTST[3]> 0) ++neff_no_cut2_xoy[i][j];
						}
		       
					} 
                       
                /*
				
				  if ((i-1)*latox <= x1 && x1 < i*latox &&
                      (j-1)*latoy <= y1 && y1 < j*latoy) {
                       ++nevcellstrk1[i][j]; 
                       }
                  
                  if ((i-1)*latox <= x2 && x2 < i*latox &&
                      (j-1)*latoy <= y2 && y2 < j*latoy) {
                       ++nevcellstrk2[i][j];
                      
                       }
				*/
				
                  }	// chiusura calcoloeff


		}	// chiusura if trackingOK == 4
		
		
		

		distT2x = distT2y = -5000.;
		distT1x = distT1y = -5000.;
              
		
		if (trackingOK == 4){
			// printf("\nil tracking ha agito. c'e' qualcosa?\n");
			// for(int c = 0; c < npiani;c++) printf("\nprima dell'if dell'eff, istrip[%d][1] vale %d",c, istrip[c][1]);
			// for(int d = 0; d < npiani;d++) printf("\nprima dell'if dell'eff, numclu[%d] vale %d",d, numclu[d]);
			// printf("\nprima dell'if dell'eff, numclu[1] vale %d", numclu[1]);
		  
		 
			if (istripTST[0][1]> 0 && (istripTST[1][1]>0 ) && ((calcoloeff==1) || (numcluTST[0] ==1 && numcluTST[1] == 1))){
		 
				bool selection =0;
				float tolerance1x, tolerance1y;
				float xT1_temp, yT1_temp;
				//for(int c = 0; c < npiani;c++)  printf("\nprima del for sui cl x, istrip[%d][1] vale %d",c, istrip[c][1]);
				
				for(int clx =1; clx <= numcluTST[0]; clx++){	// faccio n giri quanti sono i cluster del primo piano 
		                                          
					int indexclx = 1;
					
					//cout << "inizio ciclo for su clt" <<endl;
					for (int clt=1; clt <= clx-1; clt++){
						indexclx += clusizeTST[0][clt];		// salvo in indexclx la cluster size totale (somma di tutti i cluster analizzati fino ad ora)
						//cout << "clusizeTST = " << clusizeTST[0][clt] << endl;
						//cout << "indexclx = " << indexclx << endl;
					}       
					//cout << "fine ciclo for su clt" <<endl;
					
					
					if (istripTST[0][indexclx]<= 8){
						xT1_temp = ypitch1 * (istripTST[0][indexclx] + clusizeTST[0][clx] / 2. - 1.) + xoffT1[0];
					}
					if (istripTST[0][indexclx]> 8 && istripTST[0][indexclx] < 33){
                    	xT1_temp = 2 * ypitch1 * (istripTST[0][indexclx] + clusizeTST[0][clx] / 2. -4 - 1.) + xoffT1[0];
					}
						  
					
					//xT1_temp = 2 * ypitch1[0] * (istripTST[0][indexclx] + clusizeTST[0][clx] / 2.  - 1.) + xoffT1[0];
					
					//xT1_temp = ypitch1[0] * (istripTST[0][indexclx] + clusizeTST[0][clx] / 2. - 1.) + xoffT1[0];	// come strip colpita prendo quella relativa all'ultimo cluster
					//cout << "xT1_temp = " << xT1_temp << endl;
							   
						   
						       
					for(int cl1 =1; cl1 <= numcluTST[1]; cl1++){		// faccio n giri quanti sono i cluster del secondo piano
						
						int indexcl1 = 1;
						
						for (int clt1=1; clt1<= cl1-1; clt1++) indexcl1 += clusizeTST[1][clt1];		// salvo in indexcl1 la cluster size totale

						if (istripTST[0][indexclx]<33){
						    
							yT1_temp = 2 * xpitch1 * (istripTST[1][indexcl1] + clusizeTST[1][cl1] / 2. - 1.) + yoffT1[0];
							
							
							//yT1_temp = xpitch1[0] * (istripTST[1][indexcl1] + clusizeTST[1][cl1] / 2. - 1.) + yoffT1[0];	// prendo sempre la strip colpita dell'ultimo cluster
						   
						   
							/*if(numclu[1] + numclu[2]+ numclu[3]> 1)  */	//printf( "\nCluster 0-%d, 1-%d : strips %d, %d" , clx, cl1, istrip[0][indexclx], istrip[1][indexcl1]);
							/*if(numclu[1] + numclu[2]+ numclu[3]> 1) */	//printf ("  \nx= %f", xT1_temp);
							/*if(numclu[1] + numclu[2]+ numclu[3]> 1)*/	//printf ("  \ny= %f", yT1_temp);
							
							if ((!selection) || (xT1_temp - xtest1) * (xT1_temp - xtest1) + (yT1_temp - ytest1) * (yT1_temp - ytest1) 
								<(xT1 - xtest1) * (xT1 - xtest1) + (yT1 - ytest1) * (yT1 - ytest1)) {	// controllo se la posizione del nuovo hit sulla camera di test 
																										// (xyT_temp) e' piu' vicina alla posizione attesa (xy_test)
																										// rispetto all'hit precedente (xyT)
																																			
									xT1 = xT1_temp;			// se e' cosi' sovrascrivo il vecchio hit con il nuovo,
									yT1 = yT1_temp;			// che usero' poi per calcolare l'offset della camera di test rispetto alle camere di tracking
									
									if (istripTST[0][indexclx]<= 8) tolerance1x = 45.;
									else tolerance1x = 72.;
									tolerance1y = 72.;
									
									selection = 1;
							}
						}
					} 
			          		         		     
					/*  for(int cl3 =1; cl3 <= numclu[3]; cl3++){
							int indexcl3 =1;
                                                        for (int clt=1 ;clt<= cl3-1; clt++) indexcl3 += clusize[3][clt];
							if(istrip[0][indexclx]> 40 && istrip[0][indexclx] <= 64 ){
							yT1_temp =  0.5 * xpitch1[0] * (istrip[3][indexcl3] + clusize[3][cl3] / 2. - 1.) + yoffT1[0];
		                                	printf( "\nCluster 0-%d, 3-%d : strips %d, %d" , clx, cl3, istrip[0][indexclx], istrip[3][indexcl3]);
			                                printf ("  \nx= %f", xT1_temp);
			                                printf ("  \ny= %f", yT1_temp);
								if ((!selection) || (xT1_temp - xtest1) * (xT1_temp - xtest1) + (yT1_temp - ytest1) * (yT1_temp - ytest1) 
                                                                                <(xT1 - xtest1) * (xT1 - xtest1) + (yT1 - ytest1) * (yT1 - ytest1)) {
                                                                       xT1 = xT1_temp;
								       yT1 = yT1_temp;
								       tolerance1x = 32.;
								       tolerance1y = 64.;
                                       selection =1;
                            	}
							}
						}
					*/
					        	
				}	// chiusura ciclo for sui cluster del primo piano
						       
                                                        
                                         
				if (selection){
					//if(numclu[1] + numclu[2]> 1) printf("\nScelgo xT1 = %f, yT1 = %f", xT1, yT1);
					distT1x = xtest1 - xT1;			// differenza tra la x della camera di test ricostruita dalla traccia e la x dell'hit sulla camera di test

					distT1y = ytest1 - yT1;			// vengono usate per calcolare l'offset della camera di test rispetto a quelle di tracking
                         
					//printf("\nle distanze sono: x->%f, y->%f",distT1x,distT1y);
					//printf("\nselection vale: %d",selection);
					
					if(calcoloeff){
						
						if (fabs(distT1x) < tolerance1x && fabs(distT1y) < tolerance1y){
							// printf("\n ho passato il controllo sulla tolleranza");
                        
							for (int i = 1; i <= ncellsx; i++) for (int j = 1; j <= ncellsy; j++){
								if ((i-1)*lato1x + xoffT1[0] <= xtest1 && xtest1 < i*lato1x + xoffT1[0] && (j-1)*lato1y +yoffT1[0]<= ytest1 && ytest1 < j*lato1y+yoffT1[0]) {
									++neffcellstst1[i][j];
									cameraineff1 = 0.;
									//  printf("\nxteo: %f, yteo: %f,  xT1: %f,yT1: %f,  i: %d, j: %d", xtest1, ytest1, xT1, yT1, i, j);
									//  printf("\n ora ho incrementato l'efficienza di tst 1");
								}
								
							} 
							 
						}
						
					}	// chiusura if calcoloeff
					
				}	// chiusura if selection
				
			}	// chiusura if istrip[0][1]> 0 && istrip[1][1]>0 && (calcoloeff==1 || (numclu[0] ==1 && numclu[1] == 1))
			
			
			
			
			
			if ((istripTST[2][1]> 0 && istripTST[3][1]>0) && ((calcoloeff==1) ||(numcluTST[2] ==1 && numcluTST[3] == 1))){
		 
				bool selection2 =0;
				float tolerance2x, tolerance2y;
				float xT2_temp, yT2_temp;
				// for(int c = 0; c < npiani;c++)  printf("\nprima del for sui cl x, istrip[%d][1] vale %d",c, istrip[c][1]);
				
				for(int clx2 =1; clx2 <= numcluTST[2]; clx2++){
		                                          
					int indexclx2 =1;
					
					for (int clt2=1; clt2 <= clx2-1; clt2++) indexclx2 += clusizeTST[2][clt2];
						
						if (istripTST[2][indexclx2]<= 8){
							xT2_temp = ypitch2 * (istripTST[2][indexclx2] + clusizeTST[2][clx2] / 2. - 1.) + xoffT2[0];
						}
						
						if (istripTST[2][indexclx2]> 8 && istripTST[2][indexclx2]< 33 ){
                        	xT2_temp = 2 * ypitch2 * (istripTST[2][indexclx2] + clusizeTST[2][clx2] / 2. -4 - 1.) + xoffT2[0];
						}
						
						
						//xT2_temp = 2 * ypitch2[0] * (istripTST[2][indexclx2] + clusizeTST[2][clx2] / 2.  - 1.) + xoffT2[0];
						       
						       
						//xT2_temp = 2 * ypitch2[0] * (istripTST[2][indexclx2] + clusizeTST[2][clx2] / 2.  - 1.-1.) + 16. + xoffT2[0];
						   
						//if (istripTST[2][indexclx2] == 1 && clusizeTST[2][clx2] == 1 ) xT2_temp =  16./2.+ xoffT2[0];							
						//if (istripTST[2][indexclx2] == 24 && clusizeTST[2][clx2] == 1) xT2_temp =  22 * 2 * ypitch2[0] + 16*1.5 + xoffT2[0];	

						       
						for(int cl4 =1; cl4 <= numcluTST[3]; cl4++){
							
							int indexcl4 = 1;
							
							for (int clt4=1; clt4<= cl4-1; clt4++) indexcl4 += clusizeTST[3][clt4];
							
							if (istripTST[2][indexclx2]< 33){
								
								yT2_temp = 2 * xpitch2 * (istripTST[3][indexcl4] + clusizeTST[3][cl4] / 2. - 1.) + yoffT2[0];
								
								
								//yT2_temp =    2 * xpitch2[0] * (istripTST[3][indexcl4] + clusizeTST[3][cl4] / 2.  - 1.- 1.) + 16. + yoffT2[0];
						   
								
								//if (istripTST[3][indexcl4] == 1 && clusizeTST[3][cl4] == 1 ) yT2_temp =  16./2.+ yoffT2[0];								// ?????????????
								//if (istripTST[3][indexcl4] == 24 && clusizeTST[3][cl4] == 1) yT2_temp =  22 * 2 * ypitch2[0] + 16*1.5 + yoffT2[0];		// ?????????????

							
								//if(numclu[1] + numclu[2]+ numclu[3]> 1)  */	//printf( "\nCluster 2-%d, 3-%d : strips %d, %d" , clx2, cl4, istrip[2][indexclx2], istrip[3][indexcl4]);
								//if(numclu[1] + numclu[2]+ numclu[3]> 1) */	//printf ("  \nx= %f", xT2_temp);
								//if(numclu[1] + numclu[2]+ numclu[3]> 1)*/	//printf ("  \ny= %f", yT2_temp);
						
								if ((!selection2) || (xT2_temp - xtest2) * (xT2_temp - xtest2) + (yT2_temp - ytest2) * (yT2_temp - ytest2) 
									<(xT2 - xtest2) * (xT2 - xtest2) + (yT2 - ytest2) * (yT2 - ytest2)){

										xT2 = xT2_temp;
										yT2 = yT2_temp;
										if (istripTST[2][indexclx2]<= 8) tolerance2x = 45.;
										else tolerance2x = 72.;
										tolerance2y = 72.;
										
										
										selection2 = 1;
								}
							              
							}
								    
						} 
								    
						     /*
							 for(int cl3 =1; cl3 <= numclu[3]; cl3++){
							 int indexcl3 =1;
                                                        for (int clt=1 ;clt<= cl3-1; clt++) indexcl3 += clusize[3][clt];
								if(istrip[0][indexclx]> 40 && istrip[0][indexclx] <= 64 ){
									yT1_temp =  0.5 * xpitch1[0] * (istrip[3][indexcl3] + clusize[3][cl3] / 2. - 1.) + yoffT1[0];
		                            printf( "\nCluster 0-%d, 3-%d : strips %d, %d" , clx, cl3, istrip[0][indexclx], istrip[3][indexcl3]);
			                        printf ("  \nx= %f", xT1_temp);
			                        printf ("  \ny= %f", yT1_temp);
									
									if ((!selection) || (xT1_temp - xtest1) * (xT1_temp - xtest1) + (yT1_temp - ytest1) * (yT1_temp - ytest1) 
                                                                               <(xT1 - xtest1) * (xT1 - xtest1) + (yT1 - ytest1) * (yT1 - ytest1)) {
                                       xT1 = xT1_temp;
								       yT1 = yT1_temp;
								       tolerance1x = 32.;
								       tolerance1y = 64.;
                                       selection =1;
                                	}
								}
						    }
							*/
					        	
					}
						       
                                                        
                                         
					if (selection2){
					
                 		//if(numclu[1] + numclu[2]> 1) printf("\nScelgo xT2 = %f, yT2 = %f", xT2, yT2);
						
						distT2x = xtest2 - xT2;
						distT2y = ytest2 - yT2;
                         
						//printf("\nle distanze sono: x->%f, y->%f",distT2x,distT2y);
						// printf("\nselection2 vale: %d",selection2);
						if(calcoloeff){
							
							if (fabs(distT2x) < tolerance2x && fabs(distT2y) < tolerance2y){ 
								// printf("\n ho passato il controllo sulla tolleranza");
                        
								for (int i = 1; i <= ncellsx; i++) for (int j = 1; j <= ncellsy; j++){
								
									if ((i-1)*lato2x + xoffT2[0] <= xtest2 && xtest2 < i*lato2x + xoffT2[0] &&
										(j-1)*lato2y + yoffT2[0] <= ytest2 && ytest2 < j*lato2y + yoffT2[0]) {
											
											++neffcellstst2[i][j];
											cameraineff2 = 0.;
											//  printf("\nxteo: %f, yteo: %f,  xT2: %f,yT2: %f,  i: %d, j: %d", xtest2, ytest2, xT2, yT2, i, j);
											//  printf("\n ora ho incrementato l'efficienza di tst2");
									}
								
								}
														
							}
						
						}	// chiusura if calcoloeff
					
					}	// chiusura if selection2
				
				}	// chiusura if (istrip[2][1]> 0 && istrip[3][1]>0) && (calcoloeff==1 ||(numclu[2] ==1 && numclu[3] == 1))    
                    
				
				
				
				
				var.hisvar[cameraineff1Offset] = cameraineff1;
				var.hisvar[cameraineff2Offset] = cameraineff2;
			
			
			
			}	// chiusura if trackingOK == 4 


			var.hisvar[x1Offset] = x1;					// tst1xymm
			var.hisvar[y1Offset] = y1;					// tst1xymm
			var.hisvar[x2Offset] = x2;					// tst2xymm
			var.hisvar[y2Offset] = y2;					// tst2xymm
			
			var.hisvar[xtest1Offset] = xtest1;			// Ptst1xymm
			var.hisvar[ytest1Offset] = ytest1;			// Ptst1xymm
			
			var.hisvar[xtest2Offset] = xtest2;			// Ptst2xymm
			var.hisvar[ytest2Offset] = ytest2; 			// Ptst2xymm
              
			var.hisvar[xT1Offset] = xT1;				// Ptrk1xymm
			var.hisvar[yT1Offset] = yT1;				// Ptrk1xymm
			
			var.hisvar[distT1xOffset] = distT1x;		// OffsetT1x
			var.hisvar[distT1yOffset] = distT1y;		// OffsetT1y

			var.hisvar[xT2Offset] = xT2;				// Ptrk2xymm
			var.hisvar[yT2Offset] = yT2;				// Ptrk2xymm
			
			var.hisvar[distT2xOffset] = distT2x;		// OffsetT2x
			var.hisvar[distT2yOffset] = distT2y;		// OffsetT2y


			//if (trackingOK == 4) {
			
			fillhis ();

			//}
			
			AnalyzedEvent++;
	
			
			
			
			
				
		}	//	chiusura if eq_id=60
		
		

		
		
		
		
		
	
	}	//	chiusura while sulla presenza di eventi da leggere
	
	
	infile.close (); 	// chiusura file input data
	
	
}	//	chiusura ciclo for sul numero di run
  
  
  
cout<<"Fine lettura dati"<<endl<<endl;
	
	
for(int i=0; i<npianiTST; i++) {
	if(numEv!=0){
		effTST[i] = (float)neffTST[i]/(float)numEv;
	}
	else{
		effTST[i] = -1.;
	}
		
	printf("neffTST[%d] = %d,	effTST[%d] = %f \n", i, neffTST[i], i, effTST[i]);
	//fprintf(fout,"neff[%d]=%d,eff[%d] by coincidence register= %f \n",i,neff[i],i,eff[i]);
}
	
	
	
  
	
	
	
	
	
	
	
	
	
	
	
	
	/*
	cout<<endl<<"nTRK1x = "<<nTRK1x<<endl;
	cout<<"nTRK1y = "<<nTRK1y<<endl;
	cout<<"nTRK1 = "<<nTRK1<<endl<<endl;
	
	cout<<"nTRK2x = "<<nTRK2x<<endl;
	cout<<"nTRK2y = "<<nTRK2y<<endl;
	cout<<"nTRK2 = "<<nTRK2<<endl<<endl;
	
	cout<<"nTST1x = "<<nTST1x<<endl;
	cout<<"nTST1y = "<<nTST1y<<endl;
	cout<<"nTST1 = "<<nTST1<<endl<<endl;
	
	cout<<"nTST2x = "<<nTST2x<<endl;
	cout<<"nTST2y = "<<nTST2y<<endl;
	cout<<"nTST2 = "<<nTST2<<endl<<endl;
	*/
	
	
	float 		effcellstst1[260][260],effcellstst2[260][260];
	float 		erreffcellstst1[260][260], erreffcellstst2[260][260],eff_no_cut1[260][260],erreff_no_cut1[260][260],
				effstrip_1Y[260][260],erreffstrip_1Y[260][260],effstrip_1X[260][260],erreffstrip_1X[260][260],eff_no_cut2[260][260],erreff_no_cut2[260][260],
				effstrip_2Y[260][260],erreffstrip_2Y[260][260],effstrip_2X[260][260],erreffstrip_2X[260][260], eff_no_cut1_xoy[260][260],
				eff_no_cut2_xoy[260][260]; //modified

	for (int i = 1; i <= ncellsx; i++)  for (int j = 1; j <= ncellsy; j++){

		if ( nevcellstst1[i][j] != 0) {
				
			eff_no_cut1[i][j] = (float)neff_no_cut1[i][j]/(float)nevcellstst1[i][j];
			erreff_no_cut1[i][j] = sqrt((eff_no_cut1[i][j]*(1.-eff_no_cut1[i][j]))/(float) nevcellstst1[i][j]);
			effcellstst1[i][j] = (float)neffcellstst1[i][j]/(float)nevcellstst1[i][j];
			erreffcellstst1[i][j] = sqrt((effcellstst1[i][j]*(1.-effcellstst1[i][j]))/(float) nevcellstst1[i][j]);
			effstrip_1X[i][j] = (float)neffstrip_1X[i][j]/(float)nevcellstst1[i][j];
			erreffstrip_1X[i][j] = sqrt((effstrip_1X[i][j]*(1.-effstrip_1X[i][j]))/(float) nevcellstst1[i][j]);
			effstrip_1Y[i][j] = (float)neffstrip_1Y[i][j]/(float)nevcellstst1[i][j];
			erreffstrip_1Y[i][j] = sqrt((effstrip_1Y[i][j]*(1.-effstrip_1Y[i][j]))/(float) nevcellstst1[i][j]);
			eff_no_cut1_xoy[i][j] = (float)neff_no_cut1_xoy[i][j]/(float)nevcellstst1[i][j];	//modified
			
		}
		
		else{
			
			eff_no_cut1[i][j]= -1;
			erreff_no_cut1[i][j]= -1;
			effcellstst1[i][j] = -1;
			erreffcellstst1[i][j] = -1;
			effstrip_1Y[i][j] = -1;
			erreffstrip_1Y[i][j] = -1;
			effstrip_1X[i][j] = -1;
			erreffstrip_1X[i][j] = -1;
			eff_no_cut1_xoy[i][j]= -1;	//modified
			
		}

		printf("\n neffcellstst2[%d][%d] = %f\n nevcellstst2[%d][%d] = %d\n" ,i, j, effcellstst2[i][j], i, j, nevcellstst2[i][j]);

		if ( nevcellstst2[i][j] != 0) {
			
			effcellstst2[i][j] = (float)neffcellstst2[i][j]/(float)nevcellstst2[i][j];
			erreffcellstst2[i][j] = sqrt((effcellstst2[i][j]*(1.-effcellstst2[i][j]))/ (float)nevcellstst2[i][j]);
			eff_no_cut2[i][j] = (float)neff_no_cut2[i][j]/(float)nevcellstst2[i][j];
			erreff_no_cut2[i][j] = sqrt((eff_no_cut2[i][j]*(1.-eff_no_cut2[i][j]))/(float) nevcellstst2[i][j]);
			effstrip_2X[i][j] = (float)neffstrip_2X[i][j]/(float)nevcellstst2[i][j];
			erreffstrip_2X[i][j] = sqrt((effstrip_2X[i][j]*(1.-effstrip_2X[i][j]))/(float) nevcellstst2[i][j]);
			effstrip_2Y[i][j] =(float)neffstrip_2Y[i][j]/(float)nevcellstst2[i][j];
			erreffstrip_2Y[i][j] = sqrt((effstrip_2Y[i][j]*(1.-effstrip_2Y[i][j]))/(float) nevcellstst2[i][j]);
			eff_no_cut2_xoy[i][j] = (float)neff_no_cut2_xoy[i][j]/(float)nevcellstst2[i][j];	//modified
		}
        
		else{
		
			eff_no_cut2[i][j]= -1;
			erreff_no_cut2[i][j]= -1;
			effcellstst2[i][j] = -1;
			erreffcellstst2[i][j] = -1;
			effstrip_2Y[i][j] = -1;
			erreffstrip_2Y[i][j] = -1;
			effstrip_2X[i][j] = -1;
			erreffstrip_2X[i][j] = -1;
			eff_no_cut2_xoy[i][j]= -1;	//modified
		}
	
	}	// chiusura ciclo for sulle celle
	
	
	
	
	fprintf (fout, "*******************************************************\n");
	fprintf (fout, "*******************************************************\n");
	fprintf (fout, "****                                               ****\n");
	fprintf (fout, "****                 STAMPE FINALI                 ****\n");
	fprintf (fout, "****                                               ****\n");
	fprintf (fout, "*******************************************************\n");
	fprintf (fout, "*******************************************************\n");

	
	printf("\nAnalyzedEvents = %d\n\n", AnalyzedEvent);
	fprintf(fout,"\nAnalyzedEvents = %d\n\n", AnalyzedEvent);
	 
	printf("\nTrackedEvents = %d\n\n", nevtracked);
	fprintf(fout,"\nTrackedEvents = %d\n\n", nevtracked);
	
	   
	fprintf(fout, "\n\n\nEfficienze celle.\n\nCelle test 1, dimensioni %f x %f\n", lato1x, lato1y);
 
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",effcellstst1[i][j]);
		//printf( "i = %d, j = %d eff1: %3.2f\n",i, j, effcellstst1[i][j]);
		fprintf(fout, "\nCella %d, %d: eff1 =  %f +/- %f\n",i,j,effcellstst1[i][j],erreffcellstst1[i][j]);
	}
	
	 
	fprintf(fout, "\nCelle test 2, dimensioni %f x %f\n", lato2x, lato2y);
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",effcellstst2[i][j]);
		//printf( "i = %d, j = %d eff2: %3.2f\n",i,j,effcellstst2[i][j]);
		fprintf(fout, "\nCella %d, %d: eff2 =  %f +/- %f\n",i,j,effcellstst2[i][j],erreffcellstst2[i][j]);
	}   
                               
  
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",erreffcellstst1[i][j]);
		fprintf(fout, "i = %d, j = %d err1: %3.2f\n",i, j, erreffcellstst1[i][j]); 
	} 
                               
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",erreffcellstst2[i][j]);
		fprintf(fout, "i = %d, j = %d err2: %3.2f\n",i,j,erreffcellstst2[i][j]); 
	} 
	
			       
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		 fprintf(fouteff, "%d\n", nevcellstst1[i][j]);
		 fprintf(fout, "i = %d, j = %d nevcellstst1 = %d\n", i, j, nevcellstst1[i][j]);
	} 
                               
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		 fprintf(fouteff, "%d\n", nevcellstst2[i][j]);
		 fprintf(fout, "i = %d, j = %d nevcellstst2 = %d\n", i, j, nevcellstst2[i][j]);
	}			       
			       
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",eff_no_cut1[i][j]);
		fprintf(fout, "i = %d, j = %d eff_no_cut1: %3.3f\n",i, j, eff_no_cut1[i][j]); 
	} 
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",erreff_no_cut1[i][j]);
		fprintf(fout, "i = %d, j = %d err_no_cut1: %3.3f\n",i, j, erreff_no_cut1[i][j]); 
	}
	
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",effstrip_1Y[i][j]);
		fprintf(fout, "i = %d, j = %d effstrip_1Y: %3.3f\n",i, j, effstrip_1Y[i][j]); 
	} 
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",erreffstrip_1Y[i][j]);
		fprintf(fout, "i = %d, j = %d erreffstrip_1Y: %3.3f\n",i, j, erreffstrip_1Y[i][j]); 
	}
	 
	
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",effstrip_1X[i][j]);
		fprintf(fout, "i = %d, j = %d effstrip_1X: %3.3f\n",i, j, effstrip_1X[i][j]); 
	} 

	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",erreffstrip_1X[i][j]);
		fprintf(fout, "i = %d, j = %d erreffstrip_1X: %3.3f\n",i, j, erreffstrip_1X[i][j]); 
	}
			       
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",eff_no_cut2[i][j]);
		fprintf(fout, "i = %d, j = %d eff_no_cut2: %3.3f\n",i, j, eff_no_cut2[i][j]); 
	}
	 
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",erreff_no_cut2[i][j]);
		fprintf(fout, "i = %d, j = %d err_no_cut2: %3.3f\n",i, j, erreff_no_cut2[i][j]); 
	}

	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",effstrip_2Y[i][j]);
		fprintf(fout, "i = %d, j = %d effstrip_2Y: %3.3f\n",i, j, effstrip_2Y[i][j]); 
	} 

	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",erreffstrip_2Y[i][j]);
		fprintf(fout, "i = %d, j = %d erreffstrip_2Y: %3.3f\n",i, j, erreffstrip_2Y[i][j]); 
	} 
			       
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",effstrip_2X[i][j]);
		fprintf(fout, "i = %d, j = %d effstrip_2X: %3.3f\n",i, j, effstrip_2X[i][j]); 
	}
	 
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",erreffstrip_2X[i][j]);
		fprintf(fout, "i = %d, j = %d erreffstrip_2X: %3.3f\n",i, j, erreffstrip_2X[i][j]); 
	}
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",eff_no_cut1_xoy[i][j]);
		fprintf(fout, "i = %d, j = %d eff_no_cut1_xoy: %3.3f\n",i, j, eff_no_cut1_xoy[i][j]); 			//modified
	} 
	
	for (int i = 1 ; i<=ncellsx; i++) for (int j = 1; j<=ncellsy; j++){
		fprintf(fouteff, "%3.3f\n",eff_no_cut2_xoy[i][j]);
		fprintf(fout, "i = %d, j = %d eff_no_cut2_xoy: %3.3f\n",i, j, eff_no_cut2_xoy[i][j]); 			//modified
	} 
			       
  /*
  for (i = 1 ; i<=ncellsx; i++){
  for (j = 1; j<=ncellsy; j++)
                               fprintf(fouteff, "%d\n",nevcellstrk1[i][j]);
                                
                               }
                                
   for (i = 1 ; i<=ncellsx; i++){                           
   for (j = 1; j<=ncellsy; j++)
                               fprintf(fouteff, "%d\n",nevcellstrk2[i][j]);
                               } 
	*/
                               
	
	
	fprintf(fout, "\nncellsx: %d, ncellsy: %d\n", ncellsx, ncellsy);
	fclose (fouteff); 												// chiusura file efficienze
	fclose (fout);													// chiusura file diagnostic
	printf ("\nFor details see the output file:\n");
	printf (USER_OUTFILE, firstRun);
	printf ("\n\nThat's the end.\n\n\a");
	
	
	
	
	
	
	f->Write("",TObject::kOverwrite);
	
	
	//infile.close (); 	// chiusura file input data
	
	
	f->Close();		// chiusura file ROOT



	return 0;

}




/* ====================================================================== */

void sethis()
{

/* Local variables */
int i, nchan1, nchan2;
//int id;
float hispar[11];
char titbuf[40];
int numhist;
//int imxcnt = 0;
FILE *fp;
int npar,npar1;
char filename[41];
char line[80];
char histname[11];
TH1F *h1;
TH2F *h2;

numhist = 0;
npar=0;
npar1=0;
strcpy(filename,selfill.hist_file_name);


/*  OPEN FILE */
fp=fopen(filename,"r");
/*  READ HISTOGRAMS FILE : FOR EACH HISTOGRAM 2 CARDS ARE READ */
/*  histname, no.chan, lowedge, upperedge, no.chan, lowedge, upperedge, testno. */
/*  title (without blanks), var. address, var. address, var. type, width  */

while (npar!=-1) {
  for(i=0;i<11;i++) {
    hispar[i]=0.;
  }
  fgets(line,80,fp);
//    printf(" after reading one line: %s\n",line);
  npar=sscanf(line,"%s %f %f %f %f %f %f %f",histname,&hispar[0],
       &hispar[1],&hispar[2],&hispar[3],&hispar[4],&hispar[5],&hispar[6]);
  if(npar<0) break;
//      printf(" after scanning command line with %d param.\n",npar);
//      printf("histname = %s \n",histname);
//  for(i=0;i<npar-1;i++) printf("%-10.1f",hispar[i]);
//  printf("\n");
  fgets(line,80,fp);
//  printf(" after reading one line: %s\n",line);
  npar1=sscanf(line,"%s %f %f %f %f",titbuf,&hispar[7],&hispar[8],&hispar[9],&hispar[10]);
//      printf(" after scanning command line with %d param.\n",npar1);
//      printf(" title = %s -  params %f %f %f %f\n",titbuf,hispar[7],hispar[8],hispar[9],hispar[10]);
#if DBUG
  printf("\n");
  printf("--- up to now numhist is %d \n",numhist);
#endif
  nchan1 = (int)hispar[0];
  if(npar<7) {
    selfill.hist_test_last[numhist] = hispar[3]; }
  else  {
    selfill.hist_test_last[numhist] = hispar[6]; }
  strcpy(selfill.hist_ident[numhist],histname);
  selfill.hist_var1[numhist] = hispar[7];
  selfill.hist_var_type[numhist] = hispar[9];
  selfill.hist_weight[numhist] = hispar[10];

/*  CHECK IF MONO OR BIDI-MENSIONAL HISTOGRAM REQUIRED */
  if (hispar[3] == (float)0. || npar<7) {
    strcpy(selfill.hist_type[numhist], "MONO");
#if DBUG
    printf("hist type = %s \n",selfill.hist_type[numhist]);
    printf("no. of channels =%d\n",nchan1);
    printf("low edge = %f   upper edge = %f\n",hispar[1],hispar[2]);
    printf("variable address = %f\n",selfill.hist_var1[numhist]);
    printf("variable type = %f\n",selfill.hist_var_type[numhist]);
    printf("test no. = %f\n",selfill.hist_test_last[numhist]);
#endif
    h1 = new TH1F(histname,titbuf,nchan1,hispar[1],hispar[2]);
  } else {
    strcpy(selfill.hist_type [numhist], "BIDI");
    nchan2 = (int)hispar[3];
    selfill.hist_var2[numhist] = hispar[8];
#if DBUG
    printf("hist type = %s \n",selfill.hist_type[numhist]);
    printf("no. of channels %d min %f max %f\n",nchan1,hispar[1],hispar[2]);
    printf("no. of channels %d min %f max %f\n",nchan2,hispar[4],hispar[5]);
    printf("variables address = %f %f\n",selfill.hist_var1[numhist],selfill.hist_var2[numhist]);
    printf("variable type = %f\n",selfill.hist_var_type[numhist]);
    printf("test no. = %f\n",selfill.hist_test_last[numhist]);
#endif
    h2 = new TH2F(histname,titbuf,nchan1,hispar[1],hispar[2],
	         nchan2,hispar[4],hispar[5]);
  }
  numhist++;
  selfill.total_hist_num = (float) numhist;
#if DBUG
  printf("total no. of histograms = %f \n",selfill.total_hist_num);
#endif
}
fclose(fp);
//printf("Exiting from sethis\n");
} 


/* =================================================================== */
/* ----------------------------------------------------- */
/* ROUTINE TO READ TESTS FILE */
/* ----------------------------------------------------- */

void deftest()
{

    /* Local variables */
static int i, ihist, itest;
FILE *fp;
char filename[41],str[5],str1[5];
char line[80];
int npar;
float par[4];


/* OPEN FILE */
strcpy(filename , selfill.test_file_name);
fp=fopen(filename,"r");
npar=0;
itest=0;

while (npar!=-1) {
    for(i=0;i<4;i++) {
      par[i]=0.;
    }
    fgets(line,80,fp);
//    printf(" after reading one line: %s\n",line);
    npar=sscanf(line,"%s %f %f %f %f %s",str,&par[0],&par[1],
    &par[2],&par[3],str1);
    if(npar<0) break;
//      printf(" after scanning command line with %d param.\n",npar);
//      printf(" params. = %s %f %f %f %f %s\n",str,par[0],par[1],
//             par[2],par[3],str1);
//     strcpy(selfill.test_type+(itest<<2),str);
     strcpy(selfill.test_type [itest],str);
//     strcpy(selfill.test_parchar+(itest<<2),str1);
     strcpy(selfill.test_parchar[itest],str1);
     selfill.test_par[itest][0]=par[0];
     selfill.test_par[itest][1]=par[1];
     selfill.test_par[itest][2]=par[2];
     selfill.test_par[itest][3]=par[3];
#if DBUG
     printf("test no. %d \n",itest);
     printf("test type = %s  - test parchar = %s \n",selfill.test_type[itest],
             selfill.test_parchar[itest]);
     printf("param[0]= %f \n",selfill.test_par[itest][0]);
     printf("param[1]= %f \n",selfill.test_par[itest][1]);
     printf("param[2]= %f \n",selfill.test_par[itest][2]);
     printf("param[3]= %f \n",selfill.test_par[itest][3]);
#endif
     itest++;
}

#if DBUG
      printf(" total no. of test = %d \n",itest);
#endif

/* READ TESTS FILE : FOR EACH TEST 1 CARD IS READ */
    selfill.total_test_num = itest;


/* **  LOOP OVER ALL HISTOS */
    for (ihist = 0; ihist < selfill.total_hist_num; ihist++) {
	if (selfill.hist_test_last[ihist] != (float)0.) {
	    for (itest = 0; itest < selfill.total_test_num; itest++) {
		if (selfill.test_par[itest][0]== 
			selfill.hist_test_last[ihist]) {
		    goto L5;
		}
	    }
L5:
	    selfill.test_hist[ihist] = (float) itest+1;
#if DBUG
	    printf("ihist index =%d with test = %d\n",ihist+1,itest+1);
#endif
	}
    }

    fclose(fp);
//    printf("Exiting from deftest\n");
} 

/* ================================================================== */
/* ------------------------------------------------------------------ */
/*  ROUTINE TO FILL HISTOGRAMS */
/*  SELECTIVE FILLING IS IMPLEMENTED , FOLLOWING THE DIFFERENT TESTS */
/*  REQUIRED */
/*  TESTS ARE EXECUTED IN INCREASING ORDER ON THE VARIABLES IN */
/*  COMMON /VAR/ - VARIABLE CAN BE ROUGH DATA FROM BUFFER OR */
/*  CALCULATED VARIABLES FROM DECODING ROUTINES */

/*  THE AVAILABLE TESTS ARE THE FOLLOWING: */
/*  TEST ON A VARIABLE TO CHECK IF INSIDE OR OUTSIDE PREDEFINED WINDOW: */

/*       PARAM. 1 : TEST IDENTIFICATION NUMBER (INTEGER) */
/*       PARAM. 2 : POINTER TO VARIABLE IN COMMON /VAR/ (INTEGER) */
/*       PARAM. 3 : LOWER LIMIT OF THE WINDOW */
/*       PARAM. 4 : UPPER LIMIT OF THE WINDOW */
/*       PARAM. 5 : 'INSIDE' OR 'OUTSIDE' TO SPECIFY IF VARIABLE */
/*                  HAS TO BE IN OR OUT OF THE WINDOW (ASCII) */

/*  TEST ON TEST - ANY LOGICAL COMBINATION OF PREVIOUS TESTS IS POSSIBLE: 
*/
/*       PARAM. 1 : TEST IDENTIFICATION NUMBER (INTEGER) */
/*       PARAM. 2 : FIRST TEST NUMBER (INTEGER) */
/*       PARAM. 3 : SECOND TEST NUMBER (INTEGER) */
/*       PARAM. 4 : NOT USED */
/*       PARAM. 5 : 'AND' OR 'OR' LOGICAL FUNCTION ON THE TEST_FLAGS */

/*  TEST ON A SEQUENTIAL LIST OF TESTS */
/*  - ANY LOGICAL COMBINATION OF PREVIOUS TESTS IS POSSIBLE: */
/*       PARAM. 1 : TEST IDENTIFICATION NUMBER (INTEGER) */
/*       PARAM. 2 : FIRST TEST NUMBER (INTEGER) */
/*       PARAM. 3 : LAST TEST NUMBER (INTEGER) */
/*       PARAM. 4 : NOT USED */
/*       PARAM. 5 : 'AND' OR 'OR' LOGICAL FUNCTION ON THE TEST_FLAGS */

/*  TEST ON BIT TO CHECK IF A BIT IN A WORD IS SET : */
/*       PARAM. 1 : TEST IDENTIFICATION NUMBER (INTEGER) */
/*       PARAM. 2 : POINTER TO VARIABLE IN COMMON /VAR/ (INTEGER) */
/*       PARAM. 3 : BIT NUMBER (0-31) WHICH IS TESTED (INTEGER) */

/* ---------------------------------------------------------------------- */


void fillhis()
{

    /* System generated locals */
    int i_2, i_3;


    /* Local variables */
    int itab, itab1, i, j, k, l;
    extern /* Subroutine */ int hr1fil(), hr2fil();
    int ihist;
    int itest, ktest, ll;
    int iw, ip1, ip2;
    int tst;
    char histname[10];
    TH1F *h1;
    TH2F *h2;
    Float_t hval1,hval2;
    Float_t w;
    Int_t iadr;
    
/* Check if there are only histograms to be filled without any tests */

    if (selfill.total_test_num == 0) {
	goto L11;
    }


/* Loop over all the tests */
    for (itest = 0; itest < selfill.total_test_num; itest++) {

/*  TEST ON A VARIABLE TO BE INSIDE OR OUTSIDE A WINDOW */
	i = (int)selfill.test_par[itest][0];
	j = (int)selfill.test_par[itest][1];
	k = (int)selfill.test_par[itest][2];
//	printf("-- test no. %d - parameters 1,2,3 = %d %d %d \n",i,j,k);
	if (strcmp(selfill.test_type [itest], "WIND") == 0) {
	    if (strcmp(selfill.test_parchar [itest], "INSI") == 0) {
#if DBUG
	        printf("test no. %d  - window test\n",itest+1);
                printf("INSIDE test requested\n");
                printf("variable[%d] = %f \n",j-1,var.hisvar[j-1]);
                printf("should be inside %f and %f \n",selfill.test_par[itest][2]
                ,selfill.test_par[itest][3]);
 #endif
		if (var.hisvar[j - 1] > selfill.test_par[itest][2]  
			&& var.hisvar[j - 1] < selfill.test_par[itest][3]) {
		    selfill.test_flag[itest] = -1;
		}
	    } else {
#if DBUG
	        printf("test no. %d  - window test\n",itest+1);
                printf("OUTSIDE test requested\n");
                printf("variable[%d] = %f \n",j-1,var.hisvar[j-1]);
                printf("should be outside %f and %f\n",selfill.test_par[itest][2]
                ,selfill.test_par[itest][3]);
#endif
		if (var.hisvar[j - 1] < selfill.test_par[itest][2]  
			|| var.hisvar[j - 1] > selfill.test_par[itest][3]) {
		    selfill.test_flag[itest] = -1;
		}
	    }
#if DBUG
	    printf("test no. %d , test flag = %d\n",itest+1,selfill.test_flag[itest]);
#endif

/*  TEST IS A LOGICAL COMBINATION OF TESTS */
	} else if (strcmp(selfill.test_type[itest], "TEST") == 0) {
	    if (strcmp(selfill.test_parchar[itest], "AND") == 0) {
		selfill.test_flag[itest] = 
		selfill.test_flag[j-1] && selfill.test_flag[k-1];
#if DBUG
		printf("making AND between test %d and test %d\n",j,k);
		printf("first test flag is %d. second is %d\n",
		selfill.test_flag[j-1],selfill.test_flag[k-1]);
		printf("result of test %d is %d\n",itest+1,selfill.test_flag[itest]);
#endif
	    } else {
		selfill.test_flag[itest] = 
		selfill.test_flag[j-1] || selfill.test_flag[k-1];
	    }
#if DBUG
            printf("TEST test requested\n");
	    printf("test no. %d , test flag=%d\n",itest+1,selfill.test_flag[itest]);
#endif

/*  TEST IS A LOGICAL COMBINATION OF A SEQUENCE OF TESTS */
	} else if (strcmp(selfill.test_type[itest], "SEQT") == 0) {
	    if (strcmp(selfill.test_parchar[itest], "AND") == 0) {
		tst = selfill.test_flag[j - 1];
		if (! tst) {
		    goto L12;
		}
		i_2 = k;
		for (ktest = j + 1; ktest <= i_2; ++ktest) {
		    tst = tst && selfill.test_flag[ktest - 1];
		}
	    } else {
		tst = selfill.test_flag[j - 1];
		if (tst) {
		    goto L12;
		}
		i_2 = k;
		for (ktest = j + 1; ktest <= i_2; ++ktest) {
		    tst = tst || selfill.test_flag[ktest - 1];
		}
	    }
L12:
	    selfill.test_flag[itest] = tst;

/*  TEST IS ON A BIT SET IN A VARIABLE - THE VARIABLE SHOULD BE INTEGER */
	} else if (strcmp(selfill.test_type[itest], "BIT") == 0) {
	    iw = (int)var.hisvar[j - 1];
	    if(iw & 0x1<<k){
	      selfill.test_flag[itest] = -1;}
	    else {
	      selfill.test_flag[itest] = 0;
	    }
#if DBUG
	    printf("BIT test requested\n");
	    printf("word to be tested = %d %x\n",iw,iw);
	    printf("test no. %d - test flag = %d\n",itest,selfill.test_flag[itest]);
#endif
	} else {

/*  TEST IS NOT RECOGNIZED - ERROR MESSAGE */
            printf("Test NOT recognized : Error in Test File !!!\n");
	}
    }

/*  Loop over all histograms */
L11:
    for (ihist = 0; ihist < selfill.total_hist_num; ihist++) {
#if DBUG
       printf("\n");
       printf("ihist = %d - test_hist = %f \n",ihist+1,selfill.test_hist[ihist]);
#endif
	if (selfill.test_hist[ihist] != (float)0.) {
	    itest = (int)selfill.test_hist[ihist];
	} else {
	    itest = MAX_TEST;
	    selfill.test_flag[itest - 1] = -1;
	}
#if DBUG
        printf("ihist=%d - itest=%d\n",ihist+1,itest);
        printf("test flag = %d \n",selfill.test_flag[itest - 1]);
#endif
/*  CHECK THE FLAG AND FILL HISTOGRAMS ACCORDINGLY */
	if (selfill.test_flag[itest - 1]) {
	    strcpy(histname,selfill.hist_ident[ihist]);
	    ip1 = (int)selfill.hist_var1[ihist];
	    if (strcmp(selfill.hist_type [ihist], "MONO") == 0) {
		if (selfill.hist_var_type[ihist] >= (float)0.) {
                  h1 = (TH1F*)gDirectory->Get(histname);
                  hval1 = var.hisvar[ip1 - 1];
		  if(selfill.hist_weight[ihist]<0.) {
		    iadr=-(int)selfill.hist_weight[ihist];
		    w=var.hisvar[iadr-1];
//		    printf("variable address = %d , weight = %f\n",iadr,w);
		  }
		  else {
		    w=selfill.hist_weight[ihist];
		    if(w==0.) w=1;
//		    printf("weight = %f\n",w);
		  }
#if DBUG
	          printf("histname = %s  - variable addr = %d \n",histname,ip1);
	          printf("variable value = %f \n",hval1);
#endif
                  h1->Fill(hval1,w);
		} else {
//	          printf("1.variable addr = %d \n",ip1);
		    l = (int)var.hisvar[ip1-1];
		    i_2 = l;
//	          printf("2.variable value = %d \n",l);
//	          printf("2.variable value = %d \n",i_2);
//	          printf("2.variable value = %d \n",var.hisvar[300]);
//	          printf("2.variable value = %d \n",var.hisvar[ip1]);
//	          printf("2.variable value = %d \n",var.hisvar[ip1+1]);
                    h1 = (TH1F*)gDirectory->Get(histname);
		    for (itab = 1; itab <= i_2; ++itab) {
                   hval1 = var.hisvar[ip1 + itab - 1];
		  if(selfill.hist_weight[ihist]<0.) {
		    iadr=-(int)selfill.hist_weight[ihist];
		    w=var.hisvar[iadr + itab -1];
//		    printf("variable address = %d , weight = %f\n",iadr,w);
		  }
		  else {
		    w=selfill.hist_weight[ihist];
		    if(w==0.) w=1;
//		    printf("weight = %f\n",w);
		  }
//	          printf("3.variable addr = %d \n",ip1+itab-1);
//	          printf("4.histname = %s  - variable addr = %d \n",histname,ip1);
//	          printf("5.variable value = %f \n",hval1);
                    h1->Fill(hval1,w);
		    }
		}
	    } else {
		ip2 = (int)selfill.hist_var2[ihist];
		if (selfill.hist_var_type[ihist] >= (float)0.) {
                  h2 = (TH2F*)gDirectory->Get(histname);
                  hval1 = var.hisvar[ip1 - 1];
                  hval2 = var.hisvar[ip2 - 1];
		  if(selfill.hist_weight[ihist]<0.) {
		    iadr=-(int)selfill.hist_weight[ihist];
		    w=var.hisvar[iadr-1];
//		    printf("variable address = %d , weight = %f\n",iadr,w);
		  }
		  else {
		    w=selfill.hist_weight[ihist];
		    if(w==0.) w=1;
//		    printf("weight = %f\n",w);
		  }
#if DBUG
	          printf("histname = %s  - variable addrs = %d %d\n",histname,
	          ip1,ip2);
	          printf("variable values = %f %f \n",hval1,hval2);
#endif
                  h2->Fill(hval1,hval2);
		} else {
		    l = (int)var.hisvar[ip1 - 1];
		    ll = (int)var.hisvar[ip2 - 1];
		    i_2 = l;
		    for (itab = 1; itab <= i_2; ++itab) {
			i_3 = ll;
			for (itab1 = 1; itab1 <= i_3; ++itab1) {
                         h2 = (TH2F*)gDirectory->Get(histname);
                         hval1 = var.hisvar[ip1 + itab - 1];
                         hval2 = var.hisvar[ip2 + itab1 - 1];
//	                 printf("variable values = %f %f \n",hval1,hval2);
                         h2->Fill(hval1,hval2);
			}
		    }
		}
	    }
	}
    }
/* **   RESET TEST FLAG */

    for (i = 0; i < selfill.total_test_num; i++) {
	selfill.test_flag[i] = 0;
    }

} 

/*===========================================================================*/
void histo_init()
/*===========================================================================*/
{
/*
    static char test_stand_name[17+1] = "test_standard.las"; 
    static char hist_stand_name[17+1] = "hist_standard.las";
*/


	char test_stand_name[] = TEST_FILE_NAME;
	char hist_stand_name[] = HIST_TEMPFILE_NAME;
	strcpy (selfill.hist_file_name, hist_stand_name);
	sethis ();
	// printf("\nsono prima delle due righe coi tests, dentro histo_init");



	// SET UP TESTS //
  
	strcpy (selfill.test_file_name, test_stand_name);
	// printf("\nsono dopo le due righe coi tests, dentro histo_init");
	deftest ();
	// printf("\nsono dopo  deftest, dentro histo_init");





/*
    char test_stand_name[17+1] = "test_standard.las"; 
    char hist_stand_name[17+1] = "hist_standard.las";

    strcpy(selfill.hist_file_name, hist_stand_name);
    sethis();


//       SET UP TESTS 

    strcpy(selfill.test_file_name, test_stand_name);
    deftest();
*/




}


