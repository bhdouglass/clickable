#!/bin/bash

set -x
set -e

function docker_run {
    docker run \
        -v `pwd`/../:`pwd`/../ \
        -v $HOME/.gnupg/:$HOME/.gnupg/ \
        -w `pwd` \
        -u `id -u` \
        -e HOME=$HOME \
        -e USER=$USER \
        -e DEB_BUILD_OPTIONS=nocheck \
        --rm \
        -it clickable/build-deb:python3 $1
}

function publish {
    rm -f ../clickable_*

    # Prepare for upload and build source package
    #sed -i "s/) unstable/~$1) $1/g" debian/changelog
    sed -i "s/unstable/$1/g" debian/changelog
    docker_run "debuild -S"
    docker_run "dput ppa:bhdouglass/clickable ../clickable_*_source.changes"

    # Clean up
    docker_run "dh_clean"
    sed -i "s/$1/unstable/g" debian/changelog
}

# TODO get the launchpad build working for precise/trusty/xenial
#publish precise
#publish trusty
#publish xenial
publish bionic
#publish cosmic
