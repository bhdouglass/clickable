#!/bin/bash

sed -i 's/unstable/artful/g' debian/changelog
rm -f ../clickable_*
debuild -S
dput ppa:bhdouglass/clickable ../clickable_*_source.changes
