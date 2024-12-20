#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include<RTClib.h> 

RTC_DS3231 rtc;

/*#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10*/

#define SEALEVELPRESSURE_HPA (1013.25)
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

Adafruit_BME280 bme; // I2C
//Adafruit_BME280 bme(BME_CS); // hardware SPI
//Adafruit_BME280 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK); // software SPI

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

unsigned long delayTime;
float temp, press, humi;
//voltage; //voltage from flow sensor, not used anymore now
//int inputPin = 12; //Input pin to read voltage, not used now

void setup() {
  Wire.begin();
  Serial.begin(9600);
  //Serial.println(F("BME280 test"));

  Wire.begin();
  rtc.begin();

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Initialize display
    //Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 20);

  bool status;
  
  // default settings
  // (you can also pass in a Wire library object like &Wire2)
  status = bme.begin(0x76);

  //Serial.println(status);
  
  if (!status) {
    //Serial.println("Could not find a valid BME280 sensor, check wiring!");
    display.println("BME sensor not ok!");
    display.display();
    while (1);
  }
  
  display.clearDisplay();
  display.println("-- Default Test --");
  display.println("BME sensor ok!");
  display.display();

  delay(2000);

  display.clearDisplay();

  //--checking if DS3231 is present-----------------
  Wire.beginTransmission(0x68);
  byte busStatus = Wire.endTransmission();
  if (busStatus != 0)
  {
    display.println("DS3231 RTC is not found...!");
    display.display();
    while(1); //wait for ever
  }
  display.println("DS3231 RTC found...!");
  display.display();
  
  //Serial.println("-- Default Test --");
  delayTime = 600000; //10 min
  //delayTime = 10000; //10 sec

  delay(2000); 

  //Serial.println();
}


void loop() { 
  //printValues(); //Print values

  //Values set up for serial communication
  temp = bme.readTemperature();
  press = bme.readPressure()/100.0F;
  humi = bme.readHumidity();

  //Serial.println(dateAndTime);
  char buffer[20] = "YYYY-MM-DD hh:mm:ss";

  //voltage = analogRead(inputPin)*(3.3/4096) + 0.12;
  
  //Print data on serial monitor for python to pick up
  Serial.print(temp);
  Serial.print("x");
  Serial.print(press);
  Serial.print("x");
  //Serial.print(voltage);
  //Serial.print("x");
  Serial.println(humi);

  display.clearDisplay();
  display.setCursor(0, 20);
  display.println((rtc.now()).toString(buffer));
  display.println("Temp: " + String(temp,2) + " C");
  display.println("Press: " + String(press,2) + " mbar");
  display.println("Rel hum: " + String(humi,2) + " %");
  display.display(); 

  delay(delayTime);
}
