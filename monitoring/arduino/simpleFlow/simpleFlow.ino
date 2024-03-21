/**
 *******************************
 *
 * Version 1.0 - Hubert Mickael <mickael@winlux.fr> (https://github.com/Mickaelh51)
 *  - Clean ino code
 *  - Add MY_DEBUG mode in library
 * Version 0.2 (Beta 2) - Hubert Mickael <mickael@winlux.fr> (https://github.com/Mickaelh51)
 *  - Auto detect Oregon 433Mhz
 *  - Add battery level
 *  - etc ...
 * Version 0.1 (Beta 1) - Hubert Mickael <mickael@winlux.fr> (https://github.com/Mickaelh51)
 *
 *******************************
 * DESCRIPTION
 * This sketch provides an example how to implement a humidity/temperature from Oregon sensor.
 * - Oregon sensor's battery level
 * - Oregon sensor's id
 * - Oregon sensor's type
 * - Oregon sensor's channel
 * - Oregon sensor's temperature
 * - Oregon sensor's humidity
 *
 * Arduino UNO <-- (PIN 2) --> 433Mhz receiver <=============> Oregon sensors
 */

// Enable debug prints
//#define MY_DEBUG

#include <SPI.h>
#include <EEPROM.h>
#include <Oregon.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

int inputPinIn = A2;
int inputPinOut = A1;
float voltageIn = 0;
float voltageOut = 0;


void setup ()
{
  Serial.begin(9600);
  //Serial.println("Setup completed");
}


void loop () {
    //------------------------------------------
    //Start process new data from Oregon sensors
    //------------------------------------------
    
    /*temperatureData = bme.readTemperature();
    envHumidity = bme.readHumidity();
    

    Serial.print(humidityData);
    Serial.print("x");
    Serial.print(temperatureData);
    //Serial.print("x");
    //Serial.print(humi);
    Serial.print("x");
    Serial.print(batteryData);
    Serial.print("x");
    Serial.print(voltageIn);
    Serial.print("x");
    Serial.print(voltageOut);
    Serial.print("x");
    Serial.println(envHumidity);

    delay(60000);*/

    voltageIn = analogRead(inputPinIn)*(5/1024.);
    voltageOut = analogRead(inputPinOut)*(5/1024.);

    Serial.print(voltageIn);
    Serial.print("x");
    Serial.println(voltageOut);

    delay(5000);
    
   
}
