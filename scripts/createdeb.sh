#!/bin/sh

fpm -s python -t deb --no-python-dependencies -d python-zope.dottedname -d python-txzookeeper -d python-redis -d python-yaml -d python-cyclone -d python-twisted -d python-ws4py -a amd64 -n python-echidna setup.py
