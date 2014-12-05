#!/usr/bin/env python

import numpy as np
from aptread.aptload import ReadAPTData

pospath = "./data/R04.pos"
rngpath = "./data/test.rng"

data = ReadAPTData(pospath, rngpath)
ionlist = data.ions

print("Ion list:", ionlist)
