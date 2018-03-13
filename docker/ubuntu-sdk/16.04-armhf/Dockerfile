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

# Generated from `dpkg-architecture -a armhf`
ENV DEB_BUILD_ARCH=amd64
ENV DEB_BUILD_ARCH_BITS=64
ENV DEB_BUILD_ARCH_CPU=amd64
ENV DEB_BUILD_ARCH_ENDIAN=little
ENV DEB_BUILD_ARCH_OS=linux
ENV DEB_BUILD_GNU_CPU=x86_64
ENV DEB_BUILD_GNU_SYSTEM=linux-gnu
ENV DEB_BUILD_GNU_TYPE=x86_64-linux-gnu
ENV DEB_BUILD_MULTIARCH=x86_64-linux-gnu
ENV DEB_HOST_ARCH=armhf
ENV DEB_HOST_ARCH_BITS=32
ENV DEB_HOST_ARCH_CPU=arm
ENV DEB_HOST_ARCH_ENDIAN=little
ENV DEB_HOST_ARCH_OS=linux
ENV DEB_HOST_GNU_CPU=arm
ENV DEB_HOST_GNU_SYSTEM=linux-gnueabihf
ENV DEB_HOST_GNU_TYPE=arm-linux-gnueabihf
ENV DEB_HOST_MULTIARCH=arm-linux-gnueabihf
ENV DEB_TARGET_ARCH=armhf
ENV DEB_TARGET_ARCH_BITS=32
ENV DEB_TARGET_ARCH_CPU=arm
ENV DEB_TARGET_ARCH_ENDIAN=little
ENV DEB_TARGET_ARCH_OS=linux
ENV DEB_TARGET_GNU_CPU=arm
ENV DEB_TARGET_GNU_SYSTEM=linux-gnueabihf
ENV DEB_TARGET_GNU_TYPE=arm-linux-gnueabihf
ENV DEB_TARGET_MULTIARCH=arm-linux-gnueabihf

# env's for go
ENV GOOS=linux
ENV GOARCH=arm
ENV GOARM=7
ENV CGO_ENABLED=1
ENV PKG_CONFIG_LIBDIR=/usr/lib/arm-linux-gnueabihf/pkgconfig:/usr/lib/pkgconfig:/usr/share/pkgconfig
ENV CC=arm-linux-gnueabihf-gcc
ENV CXX=arm-linux-gnueabihf-g++
