#!/bin/sh
set -ex

# Run the attestation server
export PATH=$PATH:/usr/local/go/bin
cd /root/attestation
go run main.go -- -port 8082 &

DOCKER_RAMDISK=true dockerd &
sleep 15

DOCKER_TAG=$(docker load -qi $HOME/container.tar |
    sed -r 's/^Loaded image: (.+)$/\1/' | 
    tr -d '\n')

echo Loaded docker image tagged: $DOCKER_TAG

# Guest
docker run -d -p 127.0.0.1:8080:80/tcp $DOCKER_TAG 
caddy run


