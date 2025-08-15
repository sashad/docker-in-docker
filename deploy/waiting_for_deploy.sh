#!/bin/sh
#
FILE_TO_CHECK="/mnt/apache/do.reload"
SLEEP_INTERVAL=5

echo "Waiting while web-server is reloaded"

while [ -f "$FILE_TO_CHECK" ]; do
    echo "."
    sleep $SLEEP_INTERVAL
done
