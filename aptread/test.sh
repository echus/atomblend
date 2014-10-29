#!/bin/bash
# test.sh
# ReferenceImplementationPython
#
# Author: Anna Ceguerra
# Date: 5 March 2013
# Copyright (c) 2013 Australian Centre for Microscopy & Microanalysis (ACMM), The University of Sydney, NSW 2006 Australia. All rights reserved.

echo "/Users/anna/Documents/code/hg/ACMMcode-mainbranch/sample-data/cubicTest/AB2.rng" | python test-ORNLRNGloader.py

echo "/Users/anna/Documents/code/hg/ACMMcode-mainbranch/clara-matlab/03a_fcc.D0.404000nm.233unitcells.8component.kdtree.SRO.pos" | python test-POSloader.py

