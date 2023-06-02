FROM ubuntu:20.04 AS build

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /root
COPY Azure_CVM_Attestation-master /root
COPY build.sh /root
RUN ./build.sh

FROM scratch AS binaries
COPY --from=build /root/Attest /
COPY --from=build /root/bin/AttestationClient /
