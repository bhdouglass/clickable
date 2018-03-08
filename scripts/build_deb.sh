#!/bin/bash

rm -rf ./build/
mkdir -p ./build/tmp/

cp -r debian ./build/tmp/
cp clickable.py ./build/tmp/clickable

cd ./build/
docker run -v `pwd`:`pwd` -w `pwd` -u `id -u` --rm -it clickable/build-deb bash -c "cd tmp && dpkg-buildpackage"
