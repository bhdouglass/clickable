#!/bin/bash

# Prepare for upload and build source package
sed -i 's/unstable/artful/g' debian/changelog

debuild -S
dput ppa:bhdouglass/clickable ../clickable_*_source.changes

# Clean up
dh_clean
sed -i 's/artful/unstable/g' debian/changelog
