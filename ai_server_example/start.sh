#!/bin/sh
set -e

echo "MODEL_STORE_ENABLED=$MODEL_STORE_ENABLED"
echo "OPENCHATKIT_ENABLED=$OPENCHATKIT_ENABLED"
echo "NITRIDING_PROXY_ENABLED=$NITRIDING_PROXY_ENABLED"

if [ "$NITRIDING_PROXY_ENABLED" = "true" ]; then
    /nitriding -fqdn nitro.mithrilsecurity.io -acme -extport 8443  -intport 8080 -appwebsrv "http://127.0.0.1:8000" &
    echo "[sh] Started nitriding."
    sleep 1
fi

python /server.py

# Keep runing if server fails
count=1
while true; do
    printf "[%4d] $HELLO\n" $count
    count=$((count+1))
    sleep 60
done
