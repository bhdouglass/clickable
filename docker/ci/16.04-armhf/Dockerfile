FROM clickable/ubuntu-sdk:16.04-armhf
MAINTAINER Brian Douglass

RUN add-apt-repository ppa:bhdouglass/clickable && \
    apt-get update && \
    apt-get install -y clickable && \
    apt-get clean

ENV CLICKABLE_CONTAINER_MODE=1
