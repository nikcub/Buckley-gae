#!/bin/bash
SOURCES=(site admin)
LESS_BIN=`which lessc`
WATCHR_BIN=`which watchr`

if [ -e $LESS_BIN ]; then
	echo "Could not find less compressor"
	exit -1
done

for SRC in SOURCES
do
	if [ -e "less/$SRC.less" ]; then
		echo "Building: less/$SRC.less"
	else
		echo "Fatal: $SRC not a file"
	fi
done