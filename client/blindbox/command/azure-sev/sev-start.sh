#!/bin/sh
set -ex

# Run the attestation server
export PATH=$PATH:/usr/local/go/bin
cd /root/attestation
go run main.go &

DOCKER_RAMDISK=true dockerd &
sleep 15

DOCKER_TAG=$(docker load -qi $HOME/container.tar |
    sed -r 's/^Loaded image: (.+)$/\1/' | 
    tr -d '\n')

echo Loaded docker image tagged: $DOCKER_TAG

# Guest
docker run -p 0.0.0.0:80:80/tcp $DOCKER_TAG
