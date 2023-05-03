#!/bin/sh
set -ex

DOCKER_RAMDISK=true dockerd &
sleep 15

DOCKER_TAG=$(docker load -qi $HOME/container.tar |
    sed -r 's/^Loaded image: (.+)$/\1/' | 
    tr -d '\n')

echo Loaded docker image tagged: $DOCKER_TAG

# Guest
docker run -i -t -p 0.0.0.0:80:80/tcp $DOCKER_TAG
