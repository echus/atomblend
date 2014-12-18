#!/usr/bin/env python

import numpy as np
from aptread.aptload import APData

pospath = "./data/R04.pos"
rngpath = "./data/R04.rng"

data = APData(pospath, rngpath)
print("Length", len(data.xyz))
print("Points", data.xyz[0:5])
print("Ions", data.ionlist)
print("Atoms", data.atomlist)
print("Ranges", data.ranges)

print()
ION = 2
ionname = data.ionlist[ION]
print("Getting points for ion", ionname)
ionpoints = data.getion(ionname, data.mc, data.xyz)
print("Length", len(ionpoints))
print(ionpoints[0:5])

print()
ATOM = 1
atomname = data.atomlist[ATOM]
print("Getting points for atom", atomname)
atompoints = data.getatom(atomname, data.mc, data.xyz)
print("Length", len(atompoints))
print(atompoints[0:5])
