#!/usr/bin/env python

import numpy as np
from aptread.aptload import ReadAPTData

pospath = "./data/R04.pos"
rngpath = "./data/test.rng"

data = ReadAPTData(pospath, rngpath)
ionlist = data.ions

print("Ion list:", ionlist)
print()

ion = ionlist[0]
print("Ion:", ion)
print()

xyz = data.getion(ion)
print("Total XYZ:", len(data))
print("Ion XYZ:", len(xyz))
print(xyz[0:10])
