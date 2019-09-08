#!/bin/bash

docker run -v `pwd`:`pwd` -w `pwd` clickable/testing nosetests
