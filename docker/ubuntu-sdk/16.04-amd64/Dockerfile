FROM ubuntu:xenial
MAINTAINER Brian Douglass

RUN echo set debconf/frontend Noninteractive | debconf-communicate && \
    echo set debconf/priority critical | debconf-communicate

RUN echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu xenial main resticted multiverse universe" > /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu xenial-updates main resticted multiverse universe" >> /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu xenial-security main resticted multiverse universe" >> /etc/apt/sources.list

RUN apt-get update

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
    libqt5systeminfo5 \
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
    qml-module-ubuntu-components \
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
    qtquickcontrols2-5-dev

RUN apt-get clean
