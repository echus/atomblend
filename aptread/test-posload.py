#!/usr/bin/python
# test-POSloader.py
# ReferenceImplementationPython
#
# Author: Anna Ceguerra
# Date: 5 March 2013
# Copyright (c) 2013 Australian Centre for Microscopy & Microanalysis (ACMM), The University of Sydney, NSW 2006 Australia. All rights reserved.

from POSloader import ReadPos

pos_fn = raw_input('Enter pos filename: ')

posfile = ReadPos(pos_fn)
print posfile.numpoints
print posfile.xyz[10:15]
print posfile.cm[10:15]
