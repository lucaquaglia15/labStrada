#include <SPI.h>
#include <WiFiNINA.h>  //For wifi

//const char SSID[]     = "CERN";    // Network name
//const char PASS[]     = "";    // Network password

// Initialize the Wifi client library
//WiFiClient client;
//int status = WL_IDLE_STATUS;

//const char server[] = "128.141.90.208"; // pcald32 IP address

const int mixture = 2;  //1 = STD, 2 = ECO2, 3 = ECO3
double convFactor = 0;
double valueV, valueFlow = 0.000, valueFlowCorr;

void setup() {

  Serial.begin(9600);

  /*String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(SSID);
    //Connect to WPA/WPA2 network. Change this line if using open or WEP network:
      status = WiFi.begin(SSID, PASS);

    //wait 10 seconds for connection:
    delay(10000);
  }*/

  /*Serial.println("Setup flow measurement");
  
  if (mixture == 1) {
    Serial.println("Mixture chosen: STD");
    convFactor = 3.423;
  }

  else if (mixture == 2) {
    Serial.println("Mixture chosen: ECO2");
    convFactor = 2.186;
  }

  else if (mixture == 3) {
    Serial.println("Mixture chosen: ECO3");
    convFactor = 2.008;
  }

  Serial.println("Conversion factor is " + String(convFactor));*/
}

void loop() {
  int value = analogRead(A0);  // Output value from the flow sensor (ADC counts)

  //Serial.println(value);

  valueV = value * (5.0 / (double)1023);  // Convert to V

  Serial.println(valueV);

  //valueFlow = mVtoFlow(valueV); // Convert to l/min (in air)

  //Serial.print("x");

  //Serial.println(valueFlow);

  //valueFlowCorr = valueFlow/convFactor; // Convert to l/h (mixture)

  //Sending_To_phpmyadmindatabase(); // Upload data to db

  delay(30000);  // Wait 5 seconds
}

/*double mVtoFlow (double reading) {
  double flow = 0.000;
  flow = ((reading-0.5)/2)*((reading-0.5)/2);
  return flow*60;
}*/

/*void Sending_To_phpmyadmindatabase()   //CONNECTING WITH MYSQL
 {
   if (client.connect(server, 80)) {
    //Serial.println("connected");
    // Make a HTTP request:
    //Serial.print("GET /testcode/flow.php?voltage=");
    client.print("GET /testcode/flow.php?voltage=");     //YOUR URL
    //Serial.println(valueV);
    client.print(valueV);
    client.print("&flow=");
    //Serial.println("&flow=");
    client.print(valueFlow);
    //Serial.println(valueFlow);
    client.print("&realFlow=");
    //Serial.println("&realFlow=");
    client.print(valueFlowCorr);
    //Serial.println(valueFlowCorr);
    client.print(" ");      //SPACE BEFORE HTTP/1.1
    client.print("HTTP/1.1");
    client.println();
    client.println("Host: 128.141.90.208");
    client.println("Connection: close");
    client.println();
  } else {
    // if you didn't get a connection to the server:
    //Serial.println("connection failed");
  }
 }*/
