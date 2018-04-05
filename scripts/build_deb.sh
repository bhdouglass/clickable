#!/bin/bash

docker run \
    -v `pwd`/../:`pwd`/../ \
    -w `pwd` \
    -u `id -u` \
    -e PYBUILD_INSTALL_ARGS_python3=--install-scripts=/usr/bin/ \
    -e PYBUILD_NAME=clickable \
    --rm \
    -it clickable/build-deb:python3 \
    dpkg-buildpackage
