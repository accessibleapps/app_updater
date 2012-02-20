#!/bin/bash  
MoveToTarget() {
	#This takes to 2 arguments: source and target
        echo ""$1"  "$2""
	cp -rf "$1"/* "$2"
	rm -r "$1"
}

WaitForProcessToEnd() {
	#This takes 1 argument. The PID to wait for
	#Unlike the AutoIt version, this sleeps 1 second
	while [ $(kill -0 "$1") ]; do
    		sleep 1
  	done
}

RunApplication() {
	#This takes 1 application, the path to the thing to execute
	python "$1"
}

#our main code block
pid="$1"
SourcePath="$2"
DestPath="$3"
ToExecute="$4"
WaitForProcessToEnd $pid
MoveToTarget $SourcePath $DestPath
RunApplication $ToExecute
exit



