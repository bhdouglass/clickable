FROM ubuntu:xenial
MAINTAINER Brian Douglass

RUN echo set debconf/frontend Noninteractive | debconf-communicate && \
    echo set debconf/priority critical | debconf-communicate

RUN echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu xenial main resticted multiverse universe" > /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu xenial-updates main resticted multiverse universe" >> /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu xenial-security main resticted multiverse universe" >> /etc/apt/sources.list

RUN apt-get update

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
    libc-dev \
    isc-dhcp-client \
    net-tools \
    ifupdown \
    g++-arm-linux-gnueabihf \
    pkg-config-arm-linux-gnueabihf \
    libjsoncpp1 \
    libnet-cpp2 \
    libprocess-cpp3 \
    libqt5keychain0 \
    libqt5multimedia5-plugins \
    libqt5sql5-sqlite \
    qml-module-qt-labs-folderlistmodel \
    qml-module-qt-labs-settings \
    qml-module-qt-websockets \
    qml-module-qtbluetooth \
    qml-module-qtgraphicaleffects \
    qml-module-qtlocation \
    qml-module-qtmultimedia \
    qml-module-qtorganizer \
    qml-module-qtpositioning \
    qml-module-qtpurchasing \
    qml-module-qtqml-models2 \
    qml-module-qtqml-statemachine \
    qml-module-qtquick-layouts \
    qml-module-qtquick-localstorage \
    qml-module-qtquick-particles2 \
    qml-module-qtquick-window2 \
    qml-module-qtquick-xmllistmodel \
    qml-module-qtquick2 \
    qml-module-qtsensors \
    qml-module-qtsysteminfo \
    qml-module-ubuntu-onlineaccounts \
    qml-module-ubuntu-onlineaccounts-client \
    qmlscene \
    qt5-image-formats-plugins \
    qtchooser \
    qtdeclarative5-poppler1.0 \
    qtdeclarative5-u1db1.0 \
    qtdeclarative5-ubuntu-download-manager0.1 \
    qtdeclarative5-ubuntu-mediascanner0.1 \
    qtdeclarative5-ubuntu-push-plugin \
    qtdeclarative5-ubuntu-syncmonitor0.1 \
    qtdeclarative5-ubuntu-telephony-phonenumber0.1 \
    qtdeclarative5-ubuntu-ui-toolkit-plugin \
    qtdeclarative5-usermetrics0.1 \
    ubuntu-html5-theme \
    ubuntu-ui-toolkit-theme \
    google-mock \
    libjsoncpp-dev \
    libnet-cpp-dev \
    libprocess-cpp-dev \
    libproperties-cpp-dev \
    libqt5sensors5-dev \
    libqt5svg5-dev \
    libqt5websockets5-dev \
    libqt5xmlpatterns5-dev \
    libssl-dev \
    libunity-scopes-dev \
    qt3d5-dev \
    qt5-default \
    qtbase5-dev \
    qtconnectivity5-dev \
    qtdeclarative5-dev \
    qtdeclarative5-dev-tools \
    qtlocation5-dev \
    qtmultimedia5-dev \
    qtpim5-dev \
    qttools5-dev \
    ubuntu-sdk-qmake-extras \
    intltool \
    qttools5-dev-tools \
    oxideqt-codecs-extra \
    language-pack-en \
    click \
    qtquickcontrols2-5-dev \
    qtbase5-private-dev \
    qtdeclarative5-private-dev \
    libqt5opengl5-dev \
    mercurial \
    git

RUN apt-get clean

# Install go
RUN wget https://storage.googleapis.com/golang/go1.6.linux-amd64.tar.gz && \
    tar -xvf go1.6.linux-amd64.tar.gz && \
    mv go /usr/local && \
    ln -s /usr/include/arm-linux-gnueabihf/qt5/QtCore/5.4.1/QtCore /usr/include/ && \
    rm go1.6.linux-amd64.tar.gz

ENV CGO_ENABLED=1
