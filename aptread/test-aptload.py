#!/usr/bin/env python

import numpy as np
from aptload import ReadAPTData

#pos_fn = raw_input('Enter pos filename: ')
#rng_fn = raw_input('Enter rng filename: ')
pos_fn = "../data/R04.pos"
rng_fn = "../data/R04.rng"

data = ReadAPTData(pos_fn, rng_fn)
print data.xyz
