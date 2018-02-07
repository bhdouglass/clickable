FROM ubuntu:vivid
MAINTAINER Brian Douglass

RUN echo set debconf/frontend Noninteractive | debconf-communicate && \
    echo set debconf/priority critical | debconf-communicate

RUN sed -i 's/archive.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list
RUN dpkg --add-architecture armhf && apt-get update
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
    qt5-doc \
    language-pack-en \
    click
# go dependencies
RUN apt-get -y --force-yes --no-install-recommends install \
    qtbase5-private-dev:armhf \
    qtdeclarative5-private-dev:armhf \
    libqt5opengl5-dev:armhf \
    mercurial crossbuild-essential-armhf git
RUN apt-get clean
#Install go
RUN wget https://storage.googleapis.com/golang/go1.6.linux-amd64.tar.gz
RUN tar -xvf go1.6.linux-amd64.tar.gz
RUN mv go /usr/local
RUN ln -s /usr/include/arm-linux-gnueabihf/qt5/QtCore/5.4.1/QtCore /usr/include/
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
ENV GOOS linux
ENV GOARCH arm
ENV GOARM 7
ENV GOPATH /home/developer/gopath
ENV CGO_ENABLED 1
ENV PKG_CONFIG_LIBDIR /usr/lib/arm-linux-gnueabihf/pkgconfig:/usr/lib/pkgconfig:/usr/share/pkgconfig
ENV CC arm-linux-gnueabihf-gcc
ENV CXX arm-linux-gnueabihf-g++
