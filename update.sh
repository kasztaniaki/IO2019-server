#!/bin/bash

echo ADDING conda-forge channel AS lower priority:
conda config --append channels conda-forge

echo INSTALLING black:
conda install --name IO2019-server -c conda-forge black

echo REMOVING pymysql:
conda remove --name IO2019-server pymysql

echo INSTALLING sqlite:
conda install --name IO2019-server sqlite

echo REMOVING unnecessary packages:
conda remove --name IO2019-server pycparser
conda remove --name IO2019-server idna
conda remove --name IO2019-server cryptography
conda remove --name IO2019-server cffi
conda remove --name IO2019-server asn1crypto

echo UPDATING conda:
conda update -n base -c defaults conda
# for people who don't have black in their environment