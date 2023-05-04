#!/bin/sh
set -ex

DOCKER_RAMDISK=true dockerd &
sleep 15

# iptables rules inserted from CLI
#iptables -I DOCKER-USER -i docker0 -j DROP         UNCOMMENT BEFORE PUSH AND WHEN CLI IS READY

DOCKER_TAG=$(docker load -qi $HOME/container.tar |
    sed -r 's/^Loaded image: (.+)$/\1/' | 
    tr -d '\n')

echo Loaded docker image tagged: $DOCKER_TAG

# Guest
docker run -p 0.0.0.0:80:80/tcp $DOCKER_TAG
