# Build attestation server
FROM golang:1.20
COPY ./attestation /root/attestation
WORKDIR /root/attestation
RUN make -C tools/get-snp-report/ && \
    go build main.go

# Final image
FROM debian:bullseye
COPY --from=0 /root/attestation/main /root/attestation

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /root

COPY blindbox-image-build.sh .
RUN ./blindbox-image-build.sh

COPY ./blindbox-image-init.sh /root
CMD ./blindbox-image-init.sh
