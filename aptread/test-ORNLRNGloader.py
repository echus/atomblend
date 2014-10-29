#!/usr/bin/python
# test-ORNLRNGloader.py
# ReferenceImplementationPython
#
# Author: Anna Ceguerra
# Date: 5 March 2013
# Copyright (c) 2013 Australian Centre for Microscopy & Microanalysis (ACMM), The University of Sydney, NSW 2006 Australia. All rights reserved.

from ORNLRNGloader import ReadRng

fn = raw_input('Enter ORNL rng filename: ')
print fn

rngfile = ReadRng(fn)
print "ranges:", rngfile.rng
print "range atoms:", rngfile.rngatoms
print "n ranges:", rngfile.numrngs
print "ions:", rngfile.ions
print "n ions:", rngfile.numions
