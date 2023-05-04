FROM debian:bullseye

ARG EMBED_IMAGE_TAR

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /root

COPY ./sev-init.sh /root
COPY ./sev-start.sh /root

RUN ./sev-init.sh

COPY ${EMBED_IMAGE_TAR} /root/container.tar

CMD ./sev-start.sh
