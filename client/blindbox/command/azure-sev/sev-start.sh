#!/bin/sh
set -ex

DOCKER_RAMDISK=true dockerd &
sleep 15

# iptables rules inserted from CLI
#iptables -I DOCKER-USER -i docker0 -j DROP         UNCOMMENT BEFORE PUSH AND WHEN CLI IS READY

docker import $HOME/container.tar guest

# Guest
docker run -d -i -t -p 80:80 guest
