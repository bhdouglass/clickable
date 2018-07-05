#!/bin/bash

function docker_run {
    docker run \
        -v `pwd`/../:`pwd`/../ \
        -v $HOME/.gnupg/:$HOME/.gnupg/ \
        -w `pwd` \
        -u `id -u` \
        -e HOME=$HOME \
        -e USER=$USER \
        --rm \
        -it clickable/build-deb:python3 $1
}

rm ../clickable_*_source.changes

# Prepare for upload and build source package
sed -i 's/unstable/artful/g' debian/changelog
docker_run "debuild -S"
docker_run "dput ppa:bhdouglass/clickable ../clickable_*_source.changes"

# Clean up
docker_run "dh_clean"
sed -i 's/artful/unstable/g' debian/changelog


# TODO run this for each release & append RELEASE_NAME1 to each version number
