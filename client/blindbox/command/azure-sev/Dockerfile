FROM debian:bullseye

# Base image

ARG EMBED_IMAGE_TAR

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /root

COPY ./sev-init.sh /root

RUN ./sev-init.sh

# Start of deployment-specific content

COPY ${EMBED_IMAGE_TAR} /root/container.tar

COPY ./sev-start.sh /root

CMD ./sev-start.sh
