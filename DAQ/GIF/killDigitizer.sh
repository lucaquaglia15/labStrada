#!/bin/bash

# Check if digitizer.py is running
PIDS=$(pgrep -f digitizer.py)

if [ -z "$PIDS" ]; then
    echo "digitizer.py is not running."
    exit 0
fi

echo "digitizer.py is currently running with the following process(es):"
ps -f -p $PIDS

# Prompt for confirmation
read -p "Are you sure you want to kill digitizer.py? [y/N] " CONFIRM

if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
    kill $PIDS
    echo "digitizer.py has been killed."
else
    echo "Aborted. digitizer.py is still running."
fi