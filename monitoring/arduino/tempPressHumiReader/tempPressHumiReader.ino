#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

/*#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10*/

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme; // I2C
//Adafruit_BME280 bme(BME_CS); // hardware SPI
//Adafruit_BME280 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK); // software SPI

unsigned long delayTime;
float temp, press, humi, voltage;
int inputPin = 12;

void setup() {
  Serial.begin(9600);
  //Serial.println(F("BME280 test"));

  bool status;
  
  // default settings
  // (you can also pass in a Wire library object like &Wire2)
  status = bme.begin(0x76);  
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }
  
  //Serial.println("-- Default Test --");
  delayTime = 10000;

  //Serial.println();
}


void loop() { 
  //printValues(); //Print values

  //Values set up for serial communication
  temp = bme.readTemperature();
  press = bme.readPressure()/100.0F;
  humi = bme.readHumidity();

  voltage = analogRead(inputPin)*(3.3/4096) + 0.12;
  
  //Print data on serial monitor for python to pick up
  Serial.print(temp);
  Serial.print("x");
  Serial.print(press);
  Serial.print("x");
  Serial.print(humi);
  Serial.print("x");
  Serial.println(voltage);

  
  delay(delayTime);
}
