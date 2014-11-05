#!/usr/bin/env python

import numpy as np
from APTloader import ReadAPTData

#pos_fn = raw_input('Enter pos filename: ')
#rng_fn = raw_input('Enter rng filename: ')
pos_fn = "R04.pos"
rng_fn = "R04.rng"

data = ReadAPTData(pos_fn, rng_fn)