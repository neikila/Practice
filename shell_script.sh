#!/bin/bash
# declare STRING variable
#print variable on a screen
echo ${1} ${2}
cp input_configs/INPUTv${1}.dat INPUT.dat
python CVersionPart2.py ${2}
