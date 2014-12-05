#!/usr/bin/python
# test-POSloader.py
# ReferenceImplementationPython
#
# Author: Anna Ceguerra
# Date: 5 March 2013
# Copyright (c) 2013 Australian Centre for Microscopy & Microanalysis (ACMM), The University of Sydney, NSW 2006 Australia. All rights reserved.

from posload import POS

path = "/home/user/Blender/2.72/scripts/addons/atomblend/data/R04.pos"

posfile = POS(path)
print("Number of points:", posfile.npoints)
print("XYZ", posfile.xyz[10:15])
print("mc", posfile.mc[10:15])
