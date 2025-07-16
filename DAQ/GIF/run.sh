#!/bin/bash

#Set build directory of root cern in a temporary folder to not have a bunch of files oringinating from compilation in the folder
export ROOTBUILD_DIR=/tmp/rootCompile

#Check that three arguments are passed to bash script
if [ "$#" -ne 3 ]; then
  echo "Usage: $0 mixtureName "Comments" finalHV"
  exit 1
fi

#Get the three values and assign to variables
mixture="$1"
comments="$2"
lastHV="$3"

#Cal the python script to start the DAQ and also use this machinery to get the new run number in the bas script
#Itwill be used to run the code to convert from .txt to .root 
output=$(python3 -u digitizer.py "$mixture" "$comments" "$lastHV" | grep '^newRun=' | tail -n1)

#Info to the user
printf "\n\n\n"
echo "Data taking is over, now we convert the .txt files to .root, itmay take some time, in case other users want to change the filters you can tell them it's ok"
printf "\n\n\n"

#Get run number 
run=${output#newRun=}
echo "New run number is: $run"
run=1

# 1)Count how many HV folders there are in the scan
basefolder="/home/pcald32/runs/digitizer/scan_$run"
echo $basefolder

# Get all subdirectories
shopt -s nullglob
subdirs=("$basefolder"/*/)
nSub=${#subdirs[@]}

echo "Found $nSub subdirectories, corresponding to $nSub HV points scanned"

#Directory on external drive to save .txt files after they have been converted to .root
hdd_dir="/media/pcald32/Extreme SSD/digitizer"
scan_dir_hdd="$hdd_dir/scan_$run"

if [ ! -d "$scan_dir_hdd" ]; then
    mkdir -p "$scan_dir_hdd"
    echo "Created directory: $scan_dir_hdd"
else
    echo "Directory already exists: $scan_dir_hdd"
fi

#Go through all folders of the scan
#-> convert from txt to root
#-> copy to external drive
#-> delete txt files
for nfol_path in "${subdirs[@]}"; do
    
    nfol=$(basename "$nfol_path")        # e.g. HV_1
    nfol_num=${nfol#HV_}                 # e.g. 1
    
    echo "Processing folder number: $nfol_num"
    
    root -b -q "convert2root.C+($nSub, \"$nfol_path\", \"wave_\", $nfol_num, true)"

    #Copy txt files to external hdd
    hv_folder="$scan_dir_hdd/HV_$nfol_num"

    if [ ! -d "$hv_folder" ]; then
      mkdir -p "$hv_folder"
      echo "Created directory: $hv_folder"
    else
      echo "Directory already exists: $hv_folder"
    fi

    #cp -r "$nfol_path/wave_*.txt" "$hv_folder/"
    cp -r "$nfol_path"/wave_*.txt "$hv_folder/"

    #Delete files
    if [ $? -ne 0 ]; then
        echo "ROOT could not convert the data, exiting"
        exit 1
    fi

    rm -f "$nfol_path"/wave_*.txt
    echo "Deleted wave_*.txt files in $nfol_path"
done

printf "\n\n\n"
echo "Now analyzing the data, you can find the results in $basefolder/outfile_ALICE_$run.root"
printf "\n\n\n"
