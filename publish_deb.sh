#!/bin/bash

sed -i 's/unstable/trusty/g' debian/changelog
rm -f ../clickable_*
debuild -S
dput ppa:bhdouglass/clickable ../clickable_*_source.changes

sed -i 's/trusty/xenial/g' debian/changelog
rm -f ../clickable_*
debuild -S
dput ppa:bhdouglass/clickable ../clickable_*_source.changes

sed -i 's/xenial/zesty/g' debian/changelog
rm -f ../clickable_*
debuild -S
dput ppa:bhdouglass/clickable ../clickable_*_source.changes

sed -i 's/zesty/artful/g' debian/changelog
rm -f ../clickable_*
debuild -S
dput ppa:bhdouglass/clickable ../clickable_*_source.changes
