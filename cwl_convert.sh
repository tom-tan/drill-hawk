#!/bin/bash

FILENAME=$1


if [ "$FILENAME" == "" ]; then
	echo "Usage: $0 cwl.json"
	exit 1
fi
NAME=`echo $FILENAME | sed 's/\.json//'`

if [ -f $NAME.png ]; then
	exit 0
fi

cwltool --print-dot $NAME.json > $NAME.dot
dot -Tpng $NAME.dot -o $NAME.png
