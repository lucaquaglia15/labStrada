// Enable debug prints
//#define MY_DEBUG

#include <SPI.h>
#include <EEPROM.h>
#include <Oregon.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

//Variables to hold analog input pins (input and output humidity sensor)
//Env temperature and humidity
int inputPinIn = 34, inputPinOut = 35;
float envHumi = 0, envTemp = 0, voltageIn = 0, voltageOut = 0;
float relHumiIn = 0, relHumiOut = 0;
float vSupply = 5.;

Adafruit_BME280 bme; // I2C

void setup ()
{
  Serial.begin(9600);
  //Serial.println("Setup started");

  //bool status;
  //status = bme.begin(0x76);

  /*if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }*/
  //Serial.println("Setup completed");
}


void loop () {
   
  voltageIn = analogRead(inputPinIn)*(3.3/4095.);
  relHumiIn = (1/0.0062)*((voltageIn/vSupply)-0.16);
  voltageOut = analogRead(inputPinOut)*(3.3/4095.);
  relHumiOut = (1/0.0062)*((voltageOut/vSupply)-0.16);

  //envHumi = bme.readHumidity();
  //envTemp = bme.readTemperature();

  //Print data on serial port for python to pick up
  //Serial.print(envTemp);
  //Serial.print("x");
  //Serial.print(envHumi);
  //Serial.print("x");
  Serial.print(voltageIn);
  Serial.print("x");
  Serial.print(relHumiIn);
  Serial.print("x");
  Serial.print(voltageOut);
  Serial.print("x");
  Serial.println(relHumiOut);
  //Serial.println(voltageOut);

  delay(1000); //wait 10 seconds for next measurement
}
