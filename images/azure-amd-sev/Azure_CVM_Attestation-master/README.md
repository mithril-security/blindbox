# Azure_CVM_Attestation

Run build.sh to build the attestation client binary (cpp), download and install the attestation library, and build and launch the attestation server (golang).

Query the attestation service as follows:
````
AttestClientRuntimeData = <some base64 encoded data>
curl -X POST -H 'Content-Type: application/json' -d "{\"maa_endpoint\": \"sharedeus2.eus2.test.attest.azure.net\", \"runtime_data\": \"$AttestClientRuntimeData\"}" http://localhost:8080/attest/maa
````

You can change the hostname and port in main.go before you build and launch the server.
