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

//Define pin where is 433Mhz receiver (here, pin 2)
#define MHZ_RECEIVER_PIN 2
//Define maximum Oregon sensors (here, 3 differents sensors)
#define COUNT_OREGON_SENSORS 1

//Variables to hold humidity, temperature and battery percentage
float humidityData = 0;
byte humi = 0;
float temperatureData = 0;
float batteryData = 0;
byte bat = 0;
int inputPinIn = A2;
int inputPinOut = A1;
float voltageIn = 0;
float voltageOut = 0;
float envHumidity = 0;
float envTemp = 0;

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

  //Setup received data
  attachInterrupt(digitalPinToInterrupt(MHZ_RECEIVER_PIN), ext_int_1, CHANGE);

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
    
    cli();
    word p = pulse;
    pulse = 0;
    sei();
    //Serial.println("aaaaaaa");
    if (p != 0)
    {
      //Serial.println("aaaaaaa");
        if (orscV2.nextPulse(p))
        {
            //Serial.println("aaaaaaa");
            //Decode Hex Data once
            const byte* DataDecoded = DataToDecoder(orscV2);
            //Find or save Oregon sensors's ID
            int SensorID = FindSensor(id(DataDecoded),COUNT_OREGON_SENSORS);

            // just for DEBUG
            OregonType(DataDecoded);
            channel(DataDecoded);
            temperature(DataDecoded);
            humidity(DataDecoded);
            battery(DataDecoded);

            temperatureData = temperature(DataDecoded);
            humi = humidity(DataDecoded);
            bat = battery(DataDecoded);
            humidityData = humi;
            batteryData = bat;

            voltageIn = analogRead(inputPinIn)*(5/1024.);
            voltageOut = analogRead(inputPinOut)*(5/1024.);

            envHumidity = bme.readHumidity();
            envTemp = bme.readTemperature();

              //Print data on serial monitor for python to pick up
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
              Serial.print(envHumidity);
              Serial.print("x");
              Serial.println(envTemp);
        }

    }
}
