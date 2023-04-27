#!/bin/sh
set -ex

DOCKER_RAMDISK=true dockerd &
sleep 15

# debug :) please remove me
mkdir ~/.ssh
echo \
    'ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBGIkScs6r3IaPujv7/1Sj4LdbL5trRZemf0o+vd1NJ+0kRgGru5h4lz3EVOlJMVZh9GucU46z9x0Mxi/7ORGlmY= cchudant@niko' \
    > ~/.ssh/authorized_keys
service ssh restart

sleep infinity

# Create network adapter
docker network create --driver bridge proxynet

cd $HOME/squid-proxy/squid-proxy
docker build -t squid-proxy .

docker import $HOME/container.tar guest

# Model store
# python3.9 model_store.py serve --address 0.0.0.0 &

# Squid Proxy
docker run -d -p 3128:3128 --name proxy --network proxynet squid-proxy

# Guest
iptables -t nat -A OUTPUT  -p tcp --dport 80 -j REDIRECT --to-port 12345
iptables -t nat -A OUTPUT  -p tcp --dport 443 -j REDIRECT --to-port 12345
docker run -d -i -t --network proxynet -e PROXY_SERVER=proxy -e PROXY_PORT=3128 guest
# Removed the privileged flag, this may break the iptables rules alteration but if so then this solution isn't feasible anyway.
