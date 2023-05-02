cd examples/hello-world
docker build -t box:latest .
docker image save -o box.tar box:latest
#curl -i -X POST https://localhost/enclave/image -H "Content-Type: multipart/form-data" -F "image=@box.tar" -k
