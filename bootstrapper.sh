#!/bin/bash  
#bootstrapper.sh
PIDD="$5"
while kill -0 $PIDD 2>/dev/null; do sleep 1; done
# Absolute path to this script. /home/user/bin/foo.sh
SCRIPT=$(cd ${0%/*} && echo $PWD/${0##*/})
# Absolute path this script is in. /home/user/bin
SCRIPTPATH=`dirname $SCRIPT`
POSPAR1="$1" #-l
POSPAR2="$2" #location
POSPAR3="$3" #-d
POSPAR4="$4" #directory
cp -r -f $SCRIPTPATH/$4/* $2
rm -r -f $SCRIPTPATH/$4
exit 1
