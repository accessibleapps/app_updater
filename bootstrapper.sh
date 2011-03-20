#!/bin/bash

#bootstrapper.sh
#This script was originally written in Python, but converted to BASH/AutoIt for size

PIDD="$5"
kill -0 $pid >/dev/null
# Absolute path to this script. /home/user/bin/foo.sh
SCRIPT=$(readlink -f $0)
# Absolute path this script is in. /home/user/bin
SCRIPTPATH=`dirname $SCRIPT`

POSPAR1="$1" #-l
POSPAR2="$2" #location
POSPAR3="$3" #-d
POSPAR4="$4" #directory
cp -r -f $SCRIPTPATH/$4/* $2
rm -r -f $SCRIPTPATH/$4
exit 1
