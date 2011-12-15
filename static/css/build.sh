#!/bin/bash
SOURCES="site admin"
LESS_BIN=`which lessc`
WATCHR_BIN=`which watchr`

if [ -z $LESS_BIN ]; then
	echo "Could not find less compressor"
	exit -1
fi

for SRC in $SOURCES; do
	if [ -e "less/$SRC.less" ]; then
		echo "Building: less/$SRC.less"
		$LESS_BIN "less/$SRC.less" > $SRC.css 
		$LESS_BIN "less/$SRC.less" > $SRC.min.css --compress
	else
		echo "Fatal: $SRC not a file"
	fi
done

echo "Done"