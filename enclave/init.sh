#!/bin/bash

# Configure allocator
# cat << EOF > allocator.yaml
# ---
# memory_mib: 8000
# cpu_count: 2
# EOF
# mv allocator.yaml /etc/nitro_enclaves/
# systemctl start nitro-enclaves-allocator.service && systemctl enable nitro-enclaves-allocator.service
# systemctl start docker && systemctl enable docker

# Start parent proxy
cd /root
gvisor-tap-vsock/bin/gvproxy -listen vsock://:1024 -listen unix:///tmp/network.sock &
sleep 10
curl --unix-socket /tmp/network.sock http:/unix/services/forwarder/expose -X POST -d '{"local":":443","remote":"192.168.127.2:8443"}'

nitro-cli run-enclave --cpu-count 2 --memory 8000 --enclave-cid 4 --eif-path boxed-docker.eif --debug-mode
nitro-cli console --enclave-id $(nitro-cli describe-enclaves | jq -r '.[0].EnclaveID')
