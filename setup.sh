#!/bin/bash

mkdir -p build
cp buildroot_cc.py build/buildroot_cc.py
chmod +x build/buildroot_cc.py
cp build/buildroot_cc.py /usr/bin/buildroot_cc