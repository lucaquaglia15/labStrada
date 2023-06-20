Monitoring and DAQ system for Strada delle cacce DAQ ecogas
INFN Turin laboratory

By Luca Quaglia and Sara Garetti

Project is divided in two folders, DAQ and monitoring.

The DAQ one contains the scripts to laucnh the data taking. Three types of measurements are forseen:

1) Current scan: the high voltage applied to the detector(s) is changed according to the configuration file, the absorbed current is monitored for an
amount of time decided by the user, with settable sampling frequency. The high voltage is also corrected for temperature and pressure (these data are stored
in a separate database). An arbitrary number of detectors can, in principle, be operated. Tha amount of high voltage points is also configurable.

2) Efficiency scan: so far the efficiency scan uses two classes, VME.py and TDC.py. The former is used to translate the CAEN VME lib functions from C++ to python while the latter is used to implement the functions from the CAEN TDC (V488A) used in the DAQ. For now the code (effScan.py) configures the TDCs according to the config txt file and then processes the triggers in the following way: it waits for an IRQ from any of the TDCs and then it starts the pulser through the V2718 VME bridge to veto the triggers, it processes each trigger and then removes the veto for the next event. The data is saved in a .root file in a TTree (with 3 branches, one for the strip number, one for the signal time and one which contains the number of strips in each trigger). Next step is to implement the control of the high voltage and saving the current data.

3) Stability scan: -- To be implemented --

The monitoring folder contains an Arduino code (ESP32 is used), to monitor the environmental temperature and pressure (using a BME280 sensor) and the gas
flow (with an Omron D6F-P0010A2 flow sensor) and to upload such data in a mysql database, saved locally in the DAQ machine

A simple GUI has also been developed for this project. It can be used to control (almost) all aspect of the data taking such as selecting the run type, selecting and deleteing the gas mixture and delete data from runs, both locally and on the mysql db. The GUI has been developed using the pysimplegui module and it is found in labStrada/gui/gui.py

According to the user input on the gui, the different runs are started. For the future it might be nice to also be able to control which high voltage channels are included in the run, RPC name and so on. The GUI also informs the user on the running status of the monitoring scripts (for now it doesn't prevent the user to start a run even if the monitoring scripts are not running, maybe it would be nice to implement in the future).

A small DCS UI is also being implemented (labStrada/gui/testDCS.py) just for fun and to practice with python GUI creation.
