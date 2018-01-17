FROM ubuntu:vivid
MAINTAINER Brian Douglass

RUN echo set debconf/frontend Noninteractive | debconf-communicate && \
    echo set debconf/priority critical | debconf-communicate

RUN sed -i 's/archive.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y --force-yes --no-install-recommends install gnupg ubuntu-keyring software-properties-common wget

RUN add-apt-repository -y ppa:ci-train-ppa-service/stable-phone-overlay && \
    add-apt-repository -y ppa:ubports-developers/overlay && \
    echo "deb http://repo.ubports.com vivid main" >> /etc/apt/sources.list && \
    wget -qO - http://repo.ubports.com/keyring.gpg | apt-key add - && \
    apt-get update

RUN apt-get -y --force-yes --no-install-recommends dist-upgrade
RUN apt-get -y --force-yes --no-install-recommends install \
    apt-utils \
    build-essential \
    cmake \
    dpkg-cross \
    fakeroot \
    libc-dev \
    isc-dhcp-client \
    net-tools \
    ifupdown \
    g++-arm-linux-gnueabihf \
    pkg-config-arm-linux-gnueabihf \
    ubuntu-sdk-libs \
    ubuntu-sdk-libs-dev \
    ubuntu-sdk-libs-tools \
    oxideqt-codecs-extra \
    qt5-doc \
    language-pack-en \
    click \
    webapp-container
RUN apt-get clean
