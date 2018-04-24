FROM ubuntu:xenial
MAINTAINER Brian Douglass

RUN echo set debconf/frontend Noninteractive | debconf-communicate && \
    echo set debconf/priority critical | debconf-communicate

RUN echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu xenial main resticted multiverse universe" > /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu xenial-updates main resticted multiverse universe" >> /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu xenial-security main resticted multiverse universe" >> /etc/apt/sources.list && \
    echo "deb [arch=armhf] http://ports.ubuntu.com/ubuntu-ports xenial main resticted multiverse universe" >> /etc/apt/sources.list && \
    echo "deb [arch=armhf] http://ports.ubuntu.com/ubuntu-ports xenial-updates main resticted multiverse universe" >> /etc/apt/sources.list && \
    echo "deb [arch=armhf] http://ports.ubuntu.com/ubuntu-ports xenial-security main restricted multiverse universe" >> /etc/apt/sources.list

RUN dpkg --add-architecture armhf && apt-get update

RUN apt-get -y --no-install-recommends install gnupg ubuntu-keyring software-properties-common wget -f

RUN echo "deb http://repo.ubports.com xenial main" >> /etc/apt/sources.list && \
    wget -qO - http://repo.ubports.com/keyring.gpg | apt-key add - && \
    apt-get update

RUN apt-get -y --no-install-recommends dist-upgrade
RUN apt-get -y --no-install-recommends install \
    apt-utils \
    build-essential \
    cmake \
    dpkg-cross \
    fakeroot \
    libc-dev:armhf \
    isc-dhcp-client \
    net-tools \
    ifupdown \
    g++-arm-linux-gnueabihf \
    pkg-config-arm-linux-gnueabihf \
    ubuntu-sdk-libs:armhf \
    ubuntu-sdk-libs-dev:armhf \
    ubuntu-sdk-libs-tools \
    oxideqt-codecs-extra \
    language-pack-en \
    click \
    qtquickcontrols2-5-dev:armhf \
    qtbase5-private-dev:armhf \
    qtdeclarative5-private-dev:armhf \
    libqt5opengl5-dev:armhf \
    mercurial \
    crossbuild-essential-armhf \
    git
RUN apt-get clean

# Install go
RUN wget https://storage.googleapis.com/golang/go1.6.linux-amd64.tar.gz && \
    tar -xvf go1.6.linux-amd64.tar.gz && \
    mv go /usr/local && \
    ln -s /usr/include/arm-linux-gnueabihf/qt5/QtCore/5.4.1/QtCore /usr/include/ && \
    rm go1.6.linux-amd64.tar.gz

# TODO see if there is a better location for this
ADD qt.conf /usr/bin/qt.conf

# Generated from `dpkg-architecture -a armhf`
ENV DEB_BUILD_ARCH=amd64 \
    DEB_BUILD_ARCH_BITS=64 \
    DEB_BUILD_ARCH_CPU=amd64 \
    DEB_BUILD_ARCH_ENDIAN=little \
    DEB_BUILD_ARCH_OS=linux \
    DEB_BUILD_GNU_CPU=x86_64 \
    DEB_BUILD_GNU_SYSTEM=linux-gnu \
    DEB_BUILD_GNU_TYPE=x86_64-linux-gnu \
    DEB_BUILD_MULTIARCH=x86_64-linux-gnu \
    DEB_HOST_ARCH=armhf \
    DEB_HOST_ARCH_BITS=32 \
    DEB_HOST_ARCH_CPU=arm \
    DEB_HOST_ARCH_ENDIAN=little \
    DEB_HOST_ARCH_OS=linux \
    DEB_HOST_GNU_CPU=arm \
    DEB_HOST_GNU_SYSTEM=linux-gnueabihf \
    DEB_HOST_GNU_TYPE=arm-linux-gnueabihf \
    DEB_HOST_MULTIARCH=arm-linux-gnueabihf \
    DEB_TARGET_ARCH=armhf \
    DEB_TARGET_ARCH_BITS=32 \
    DEB_TARGET_ARCH_CPU=arm \
    DEB_TARGET_ARCH_ENDIAN=little \
    DEB_TARGET_ARCH_OS=linux \
    DEB_TARGET_GNU_CPU=arm \
    DEB_TARGET_GNU_SYSTEM=linux-gnueabihf \
    DEB_TARGET_GNU_TYPE=arm-linux-gnueabihf \
    DEB_TARGET_MULTIARCH=arm-linux-gnueabihf

# env's for go
ENV GOOS=linux \
    GOARCH=arm \
    GOARM=7 \
    CGO_ENABLED=1 \
    PKG_CONFIG_LIBDIR=/usr/lib/arm-linux-gnueabihf/pkgconfig:/usr/lib/pkgconfig:/usr/share/pkgconfig \
    CC=arm-linux-gnueabihf-gcc \
    CXX=arm-linux-gnueabihf-g++
