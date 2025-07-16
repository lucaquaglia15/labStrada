#!/bin/bash

# The known string to identify your device
KNOWN_STRING="CAEN CAEN DT5xxx USB"

g++ -o usbreset usbreset.c

# Find the line in lsusb output matching the known string
DEVICE_LINE=$(lsusb | grep "$KNOWN_STRING")

if [ -z "$DEVICE_LINE" ]; then
    echo "Device not found: $KNOWN_STRING"
    exit 1
fi

# Extract the bus and device numbers
BUS=$(echo "$DEVICE_LINE" | awk '{print $2}')
DEVICE=$(echo "$DEVICE_LINE" | awk '{print $4}' | sed 's/://')

# Call usbreset
echo 'pcald32' | sudo -S ./usbreset /dev/bus/usb/$BUS/$DEVICE