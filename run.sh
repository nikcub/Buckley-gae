#!/bin/bash

# replace these paths with your own datastore

# @TODO proper virtualenv support

DS=".data/nikcub.datastore"
DH=".data/datastore.history"
BS=".data/blobstore"
IP=$2
PORT=$1
PP=`whereis python2.5`
HTTP_CLIENT=`whereis lynx`
APPSERVER="/usr/local/bin/dev_appserver.py"

if [ "$PORT" = "" ]; then 
	PORT="9090"
fi

if [ "$IP" = "" ]; then 
	IP="localhost"
fi

echo "Sketch AppEngine Helper Script" 
echo "Usage: run.sh [port] [ip] (defaults to 9090 and localhost)" 
echo "Using IP : " $IP 
echo "Using Port : " $PORT
echo "Using DS : " $DS
echo "Using DH : " $DH

echo "Starting client.. (datastore: $DS)"
$PP $APPSERVER -p $PORT -a $IP --use_sqlite --datastore_path=$DS --blobstore_path=$BS --history_path=$DH --disable_static_caching --skip_sdk_update_check .
