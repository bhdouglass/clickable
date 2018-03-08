#!/bin/bash

rm -rf ./build/
mkdir -p ./build/tmp/

cp -r debian ./build/tmp/
cp clickable.py ./build/tmp/clickable

cd ./build/

sed -i 's/unstable/artful/g' ./build/tmp/debian/changelog

cd build/tmp
debuild -S
dput ppa:bhdouglass/clickable ../clickable_*_source.changes
