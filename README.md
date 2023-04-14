Monitoring and DAQ system for Strada delle cacce DAQ ecogas
INFN Turin laboratory

By Luca Quaglia and Sara Garetti

Project is divided in two folders, DAQ and monitoring.

The DAQ one contains the scripts to laucnh the data taking. Three types of measurements are forseen:

1) Current scan: the high voltage applied to the detector(s) is changed according to the configuration file, the absorbed current is monitored for an
amount of time decided by the user, with settable sampling frequency. The high voltage is also corrected for temperature and pressure (these data are stored
in a separate database). An arbitrary number of detectors can, in principle, be operated. Tha amount of high voltage points is also configurable.

2) Efficiency scan: -- To be implemented --

3) Stability scan: -- To be implemented --

The monitoring folder contains an Arduino code (ESP32) is used, to monitor the environmental temperature and pressure (using a BME280 sensor) and the gas
flow (with an Omron D6F-P0010A2 flow sensor) and to upload such data in a mysql database, saved locally in the DAQ machine
