#!/bin/bash
# declare STRING variable
#print variable on a screen
version=${1}
if [ $# -eq 0 ] ; then
  version=0
fi
echo input_version = ${1} = $version, visual = ${2}, amount = $#
cp input_configs/INPUTv${version}.dat INPUT.dat
python CVersionPart2.py ${2}
