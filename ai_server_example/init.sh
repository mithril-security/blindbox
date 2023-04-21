#!/bin/bash
export HOME="/root"
cd /root

# Install Nitro CLI
amazon-linux-extras install aws-nitro-enclaves-cli -y
yum install aws-nitro-enclaves-cli-devel -y

# Configure allocator
cat << EOF > allocator.yaml
---
memory_mib: 110000
cpu_count: 12
EOF
mv allocator.yaml /etc/nitro_enclaves/
systemctl start nitro-enclaves-allocator.service && systemctl enable nitro-enclaves-allocator.service
systemctl start docker && systemctl enable docker

# Install Golang
wget https://go.dev/dl/go1.20.2.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.20.2.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc

# Install git
yum install git -y

# Build and install gvisor
git clone https://github.com/containers/gvisor-tap-vsock.git
cd gvisor-tap-vsock/
make
cd

# Build and install nitriding
git clone https://github.com/mithril-security/nitriding.git
cd nitriding/
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin v1.52.1
echo 'export PATH="$PATH:$(go env GOPATH)/bin"' >> ~/.bashrc 
source ~/.bashrc
make cmd/nitriding
cd

# Start parent proxy
gvisor-tap-vsock/bin/gvproxy -listen vsock://:1024 -listen unix:///tmp/network.sock &
sleep 10
curl --unix-socket /tmp/network.sock http:/unix/services/forwarder/expose -X POST -d '{"local":":443","remote":"192.168.127.2:8443"}'

# Download app
cd ~/nitriding
git clone https://github.com/mithril-security/whisper-fastapi.git
cd whisper-fastapi

# Install and start model store
python3 -m venv env
source env/bin/activate
pip install -r model_store_requirements.txt
python model_store.py download "openai/whisper-tiny.en"
python model_store.py download "togethercomputer/Pythia-Chat-Base-7B"
python model_store.py serve --address 0.0.0.0 &

# Build and start enclave app
exec make

