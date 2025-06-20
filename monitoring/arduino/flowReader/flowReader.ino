#include <SPI.h>

//const char SSID[]     = "CERN";    // Network name
//const char PASS[]     = "";    // Network password

// Initialize the Wifi client library
//WiFiClient client;
//int status = WL_IDLE_STATUS;

//const char server[] = "128.141.90.208"; // pcald32 IP address


void setup() {

  Serial.begin(9600);

}

void loop() {
  int valueOut = analogRead(26);  // Output value from the flow sensor (ADC counts)
  //int valueIn = analogRead(25);

  //Serial.println(value);

  float valueVOut = valueOut * (3.3 / (double)4095);  // Convert to V
  //float valueVIn = valueIn * (3.3 / (double)4095);  // Convert to V

  Serial.println(valueVOut);
  //Serial.println(valueVIn);

  delay(30000);  // Wait 5 seconds
}
