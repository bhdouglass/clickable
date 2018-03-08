FROM ubuntu:xenial
MAINTAINER Brian Douglass

RUN echo set debconf/frontend Noninteractive | debconf-communicate && \
    echo set debconf/priority critical | debconf-communicate

RUN apt-get update && \
    apt-get -y --force-yes --no-install-recommends install \
        debhelper \
        help2man \
        dpkg-dev \
        python3 \
        python3-cookiecutter \
        fakeroot \
        build-essential \
        && \
    apt-get clean
