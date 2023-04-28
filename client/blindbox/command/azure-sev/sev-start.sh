#!/bin/sh
set -ex

DOCKER_RAMDISK=true dockerd &
sleep 15

# iptables rules inserted from CLI
#iptables -I DOCKER-USER -i docker0 -j DROP         UNCOMMENT BEFORE PUSH AND WHEN CLI IS READY

# Create network adapter
docker network create --driver bridge proxynet

cd $HOME/squid-proxy/squid-proxy
docker build -t squid-proxy .

docker import $HOME/container.tar guest

# Model store
# python3.9 model_store.py serve --address 0.0.0.0 &

# Guest
docker run -d -i -t -p 80:80 guest
