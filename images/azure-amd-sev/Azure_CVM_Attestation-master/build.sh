#!/bin/bash

# Script must be run as sudo for installation of dependecies and for the attestation server to work correctly

# Install build dependecies for Attestation client binary
apt-get update
apt-get install build-essential libcurl4-openssl-dev libjsoncpp-dev libboost-all-dev cmake wget nlohmann-json3-dev -y

# Install attestation library from Azure
wget https://packages.microsoft.com/repos/azurecore/pool/main/a/azguestattestation1/azguestattestation1_1.0.5_amd64.deb
dpkg -i azguestattestation1_1.0.5_amd64.deb

# Build Attestation client binary
mkdir bin
cmake -B attestation_client -S attestation_client
make -C attestation_client
cp attestation_client/AttestationClient ./bin

# Install go (linux)
wget https://go.dev/dl/go1.20.4.linux-amd64.tar.gz
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.20.4.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# Compile and launch server
go mod tidy
go build
./Attest