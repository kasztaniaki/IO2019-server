#!/bin/bash

echo ADDING conda-forge channel AS lower priority:
conda config --append channels conda-forge

echo INSTALLING black:
conda install -y --name IO2019-server -c conda-forge black

echo REMOVING pymysql:
conda remove -y  --name IO2019-server pymysql

echo INSTALLING sqlite:
conda install -y  --name IO2019-server sqlite

echo REMOVING unnecessary packages:
conda remove -y --name IO2019-server pycparser
conda remove -y --name IO2019-server idna
conda remove -y --name IO2019-server cryptography
conda remove -y --name IO2019-server cffi
conda remove -y --name IO2019-server asn1crypto

echo UPDATING conda:
conda update -y -n base -c defaults conda
# for people who don't have black in their environment