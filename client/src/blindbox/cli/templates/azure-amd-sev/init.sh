#!/bin/bash

set -euo pipefail
trap 's=$?; echo >&2 "$0: Error on line "$LINENO": $BASH_COMMAND"; exit $s' ERR

cd /root

curl -o azguestattestation.deb -L https://packages.microsoft.com/repos/azurecore/pool/main/a/azguestattestation1/azguestattestation1_1.0.5_amd64.deb
dpkg -i azguestattestation.deb

curl -o Attest -L "https://github.com/mithril-security/blindbox/releases/download/v0.2.0-aaa.dev.1/Attest"
curl -o AttestationClient -L "https://github.com/mithril-security/blindbox/releases/download/v0.2.0-aaa.dev.1/AttestationClient"
chmod +x Attest AttestationClient
mkdir bin
mv AttestationClient bin/
/root/Attest
