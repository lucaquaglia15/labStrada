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
int inputPinIn = A1, inputPinOut = A2;
float envHumi = 0, envTemp = 0, voltageIn = 0, voltageOut = 0;

Adafruit_BME280 bme; // I2C

void setup ()
{
  Serial.begin(9600);
  //Serial.println("Setup started");

  bool status;
  status = bme.begin(0x76);

  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }
  //Serial.println("Setup completed");
}


void loop () {
   
  voltageIn = analogRead(inputPinIn)*(5/1024.);
  voltageOut = analogRead(inputPinOut)*(5/1024.);

  envHumi = bme.readHumidity();
  envTemp = bme.readTemperature();

  //Print data on serial port for python to pick up
  Serial.print(envTemp);
  Serial.print("x");
  Serial.print(envHumi);
  Serial.print("x");
  Serial.print(voltageIn);
  Serial.print("x");
  Serial.println(voltageOut);

  delay(10000); //wait 10 seconds for next measurement
}
