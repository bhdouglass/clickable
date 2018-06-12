FROM clickable/ubuntu-sdk:15.04-armhf
MAINTAINER Brian Douglass

# Manually download & install the debs because launchpad no longer supports vivid

RUN apt-get update && \
    apt-get install -y \
        python3-cookiecutter \
        android-tools-adb \
        docker.io && \
    apt-get clean

RUN wget https://launchpad.net/~bhdouglass/+archive/ubuntu/clickable/+files/clickable_4.2.2_all.deb && \
    dpkg -i clickable_4.2.2_all.deb && \
    rm clickable_4.2.2_all.deb
