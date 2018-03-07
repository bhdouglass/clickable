FROM clickable/ubuntu-sdk:15.04-armhf
MAINTAINER Brian Douglass

RUN cd /tmp && \
    apt-get download libsmbclient:armhf && \
    ar -x libsmbclient_*_armhf.deb && \
    tar -xvf data.tar.xz && \
    cp -r usr/* /usr && \
    rm -r /tmp/*

RUN cd /tmp && \
    apt-get download libsmbclient-dev:armhf && \
    ar -x libsmbclient-dev_*_armhf.deb && \
    tar -xvf data.tar.xz && \
    cp -r usr/* /usr && \
    rm -r /tmp/*
