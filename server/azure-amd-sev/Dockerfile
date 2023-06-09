FROM ubuntu:20.04 AS build

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /root

COPY install_deps.sh /root
RUN ./install_deps.sh

COPY src /root
RUN /usr/local/go/bin/go mod tidy -e
RUN /usr/local/go/bin/go build

FROM scratch AS binaries
COPY --from=build /root/blindbox /
# COPY --from=build /root/bin/AttestationClient /
