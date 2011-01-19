#!/bin/bash

#bootstrapper.sh
#This script was originally written in Python, but converted to BASH/AutoIt for size

POSPAR1="$1" #-l
POSPAR2="$2" #location
POSPAR3="$3" #-d
POSPAR4="$4" #directory
mv $4/* $2
