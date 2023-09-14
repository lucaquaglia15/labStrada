#include <Wire.h>

#define CLOCK_FREQUENCY 50000
#define DAC_ADDRESS 0x21
#define BOARD_NUM 6
#define BASE_COUNTS 513

//int boardAddress = 0; //Address of FEERIC board
//int boardAddress[BOARD_NUM] = {0,1,2,3};
//float thr[BOARD_NUM] = {100.0, 200.0, -350.0, -200.0};
//int thrCounts[BOARD_NUM] ={0,0,0,0};
//uint16_t finalThr[BOARD_NUM] = {0,0,0,0};
//byte LSB[BOARD_NUM] = {0,0,0,0};
//byte MSB[BOARD_NUM] = {0,0,0,0};

int boardAddress[BOARD_NUM] = {0,1,2,3,4,5};
//float thr[BOARD_NUM] = {100.0,105.0,107.0,-100,-103,-102}; //For 100 mV test beam
float thr[BOARD_NUM] = {-100,-103,-102,100,105,107}; //For lab Strada current configuration

int thrCounts[BOARD_NUM] ={0,0,0,0,0,0};
uint16_t finalThr[BOARD_NUM] = {0,0,0,0,0,0};
byte LSB[BOARD_NUM] = {0,0,0,0,0,0};
byte MSB[BOARD_NUM] = {0,0,0,0,0,0};
//int dacAddress = 0x21; //Address of DAC in board
//int clockFrequency = 50000; //50 kHz clock

float mVperCount = 2.93; //mV per DAC count
//float thr = 283.0; //desired thr
//int baseCounts = 513; //Corresponds to 0 mV
//int thrCounts = thr/mVperCount;
//uint16_t finalThr = baseCounts + thrCounts;
//byte LSB = (finalThr & 0x00FF);
//byte MSB = ((finalThr & 0xFF00) >>8);

void setup() {

  Serial.begin(9600);
  while (!Serial);
  Serial.println("Up to here 1");
  Wire.begin();
  Wire.setClock(CLOCK_FREQUENCY); //Set clock frequency as per FEERIC specs
  //Serial.begin(9600);
  //while (!Serial);
  Serial.println("Welcome to Arduino threshold setter by Luca");
  /*Serial.print(finalThr);
  Serial.print("\n");
  Serial.print(LSB);
  Serial.print("\n");
  Serial.print(MSB);
  Serial.print("\n");*/
  byte error;

  for (int i = 0; i < BOARD_NUM; i++) {
    //Convert thr to DAC counts
    thrCounts[i] = abs(thr[i])/mVperCount;

    //Sum it to the 513 baseline
    if (thr[i] >= 0) finalThr[i] = BASE_COUNTS + thrCounts[i]; //positive thr
    if (thr[i] < 0) finalThr[i] = BASE_COUNTS - thrCounts[i]; //negative thr

    //Calculate LSB and MSB to send to the DAC    
    LSB[i] = (finalThr[i] & 0x00FF);
    MSB[i] = ((finalThr[i] & 0xFF00) >> 8);

    //Begin transmission with the board    
    Wire.beginTransmission(boardAddress[i]); 
    Wire.write(00000001); //Enable DAC
    error = Wire.endTransmission();
    Serial.print("\n");
    Serial.print(error);
    Serial.print("\n");
    if (error == 0) Serial.println("Com with board started");

    Wire.beginTransmission(DAC_ADDRESS);
    Wire.write(00000000); //Send command
    Wire.write(LSB[i]); //Write LSB
    Wire.write(MSB[i]); //Write MSB

    error = Wire.endTransmission();
    if (error == 0) Serial.println("Data written to DAC");

    Wire.beginTransmission(boardAddress[i]); //Begin transmission with the board
    Wire.write(00000000); //Disable DAC
    Wire.endTransmission();
  }

  /*Serial.println("Number of boards = 1, positive thresholds = 1, negative thresholds = 0");
  Wire.beginTransmission(boardAddress); //Begin transmission with the board
  Wire.write(00000001); //Enable DAC
  error = Wire.endTransmission();
  Serial.print("\n");
  Serial.print(error);
  Serial.print("\n");
  if (error == 0) Serial.println("Com with board started");

  Wire.beginTransmission(dacAddress);
  Wire.write(00000000); //Send command*/
  //error = Wire.endTransmission();
  //if (error == 0) Serial.println("Com with DAC started");

  /*Wire.write(LSB); //Write LSB
  Wire.write(MSB); //Write MSB
  //Wire.endTransmission();
  error = Wire.endTransmission();
  if (error == 0) Serial.println("Data written to DAC");*/

  /*Wire.beginTransmission(boardAddress); //Begin transmission with the board
  Wire.write(00000000); //Disable DAC
  Wire.endTransmission();*/


  Wire.end(); //End I2C transmission
}

void loop() {
}

/*Serial.println("Number of bards = 1, positive thresholds = 1, negative thresholds = 0");
Wire.beginTransmission(boardAddress); //Begin transmission with the board
Wire.write(00000001); //Enable DAC
Wire.endTransmission();

Wire.beginTransmission(dacAddress);
Wire.write(00000000); //Send command
Wire.write(01011001); //Write LSB
Wire.write(00000010); //Write MSB
Wire.endTransmission();

Wire.beginTransmission(boardAddress); //Begin transmission with the board
Wire.write(00000000); //Disable DAC
Wire.endTransmission();


Wire.end(); //End I2C transmission*/

/*void loop() {
  //Single board -test
  //int num_boards = 1, pos_boards = 1, neg_boards = 0;

  //Multiple boards - final version
  int num_boards = 0, pos_boards = 0, neg_boards = 0;
  Serial.println("How many boards do you want to configure?");
  
  while (Serial.available() == 0) {

  }
  num_boards = Serial.parseInt();

  Serial.println("How many positive boards?");
  while (Serial.available() == 0) {

  }
  pos_boards = Serial.parseInt();

  Serial.println("How many negative boards?");
   while (Serial.available() == 0) {

  }
  neg_boards = Serial.parseInt();

}*/
