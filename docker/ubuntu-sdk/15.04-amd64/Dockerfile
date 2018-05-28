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
    webapp-container \
    qtbase5-private-dev \
    qtdeclarative5-private-dev \
    libqt5opengl5-dev \
    mercurial \
    git \
    libicu-dev \
    qtfeedback5-dev \
    qtsystems5-dev
RUN apt-get clean

# Install go
RUN wget https://storage.googleapis.com/golang/go1.6.linux-amd64.tar.gz && \
    tar -xvf go1.6.linux-amd64.tar.gz && \
    mv go /usr/local && \
    ln -s /usr/include/arm-linux-gnueabihf/qt5/QtCore/5.4.1/QtCore /usr/include/ && \
    rm go1.6.linux-amd64.tar.gz

ENV CGO_ENABLED=1
