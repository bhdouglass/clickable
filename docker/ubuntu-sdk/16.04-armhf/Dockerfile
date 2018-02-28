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

RUN add-apt-repository -y ppa:ci-train-ppa-service/stable-phone-overlay && \
    echo "deb http://repo.ubports.com xenial main" >> /etc/apt/sources.list && \
    wget -qO - http://repo.ubports.com/keyring.gpg | apt-key add - && \
    apt-get update

RUN echo \
        "Package: *"  \
        > /etc/apt/preferences.d/stable-phone-overlay.pref && \
    echo \
        "Pin: release o=LP-PPA-ci-train-ppa-service-stable-phone-overlay" \
        >> /etc/apt/preferences.d/stable-phone-overlay.pref && \
    echo \
        "Pin-Priority: 1001" \
        >> /etc/apt/preferences.d/stable-phone-overlay.pref
RUN echo \
        "Package: *" \
        > /etc/apt/preferences.d/ubports.pref && \
    echo \
        "Pin: origin repo.ubports.com" \
        >> /etc/apt/preferences.d/ubports.pref && \
    echo \
        "Pin-Priority: 2000" \
        >> /etc/apt/preferences.d/ubports.pref

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
    libjsoncpp1:armhf \
    libnet-cpp2:armhf \
    libprocess-cpp3:armhf \
    libqt5keychain0:armhf \
    libqt5multimedia5-plugins:armhf \
    libqt5sql5-sqlite:armhf \
    qml-module-qt-labs-folderlistmodel:armhf \
    qml-module-qt-labs-settings:armhf \
    qml-module-qt-websockets:armhf \
    qml-module-qtbluetooth:armhf \
    qml-module-qtgraphicaleffects:armhf \
    qml-module-qtlocation:armhf \
    qml-module-qtmultimedia:armhf \
    qml-module-qtorganizer:armhf \
    qml-module-qtpositioning:armhf \
    qml-module-qtpurchasing:armhf \
    qml-module-qtqml-models2:armhf \
    qml-module-qtqml-statemachine:armhf \
    qml-module-qtquick-layouts:armhf \
    qml-module-qtquick-localstorage:armhf \
    qml-module-qtquick-particles2:armhf \
    qml-module-qtquick-window2:armhf \
    qml-module-qtquick-xmllistmodel:armhf \
    qml-module-qtquick2:armhf \
    qml-module-qtsensors:armhf \
    qml-module-qtsysteminfo:armhf \
    qml-module-ubuntu-onlineaccounts:armhf \
    qml-module-ubuntu-onlineaccounts-client:armhf \
    qmlscene:armhf \
    qt5-image-formats-plugins:armhf \
    qtchooser:armhf \
    qtdeclarative5-poppler1.0:armhf \
    qtdeclarative5-u1db1.0:armhf \
    qtdeclarative5-ubuntu-download-manager0.1:armhf \
    qtdeclarative5-ubuntu-mediascanner0.1:armhf \
    qtdeclarative5-ubuntu-push-plugin:armhf \
    qtdeclarative5-ubuntu-syncmonitor0.1:armhf \
    qtdeclarative5-ubuntu-telephony-phonenumber0.1:armhf \
    qtdeclarative5-ubuntu-ui-toolkit-plugin:armhf \
    qtdeclarative5-usermetrics0.1:armhf \
    ubuntu-html5-theme:armhf \
    ubuntu-ui-toolkit-theme:armhf \
    google-mock:armhf \
    libjsoncpp-dev:armhf \
    libnet-cpp-dev:armhf \
    libprocess-cpp-dev:armhf \
    libproperties-cpp-dev:armhf \
    libqt5sensors5-dev:armhf \
    libqt5svg5-dev:armhf \
    libqt5websockets5-dev:armhf \
    libqt5xmlpatterns5-dev:armhf \
    libssl-dev:armhf \
    libunity-scopes-dev:armhf \
    qt3d5-dev:armhf \
    qt5-default:armhf \
    qtbase5-dev:armhf \
    qtconnectivity5-dev:armhf \
    qtdeclarative5-dev:armhf \
    qtdeclarative5-dev-tools:armhf \
    qtlocation5-dev:armhf \
    qtmultimedia5-dev:armhf \
    qtpim5-dev:armhf \
    qttools5-dev:armhf \
    qt5-qmake-arm-linux-gnueabihf \
    ubuntu-sdk-qmake-extras:armhf \
    intltool:armhf \
    qttools5-dev-tools:amd64 \
    oxideqt-codecs-extra \
    language-pack-en \
    click \
    qtquickcontrols2-5-dev:armhf

RUN apt-get clean

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
