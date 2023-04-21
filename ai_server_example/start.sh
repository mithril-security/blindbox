#!/bin/sh

set -x
set -e

/nitriding -fqdn nitro.mithrilsecurity.io -acme -extport 8443  -intport 8080 -appwebsrv "http://127.0.0.1:8000" &
echo "[sh] Started nitriding."
sleep 1

python /server.py

# Keep runing if server fails
count=1
while true; do
    printf "[%4d] $HELLO\n" $count
    count=$((count+1))
    sleep 60
done
