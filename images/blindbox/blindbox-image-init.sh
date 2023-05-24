#!/bin/bash
set -ex

/root/attestation &

if [[ -z "${INNER_IMAGE}" ]]; then
    INNER_IMAGE="hello-world"
fi

DOCKER_RAMDISK=true dockerd &
sleep 15

# iptables rules inserted from CLI
#iptables -I DOCKER-USER -i docker0 -j DROP         UNCOMMENT BEFORE PUSH AND WHEN CLI IS READY

# Guest
docker run -p 0.0.0.0:80:80/tcp "${INNER_IMAGE}"
