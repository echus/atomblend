# ORNLRNGloader.py
# ReferenceImplementationPython
#
# Author: Anna Ceguerra, Varvara Efremova
# Date: 14 April 2014
# Copyright (c) 2014 Australian Centre for Microscopy & Microanalysis (ACMM), The University of Sydney, NSW 2006 Australia. All rights reserved.

import numpy as np

# convert to int or float or remain as string
def conv(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

class RNGinfo():
    def __init__(self, rng_fn):
        self.rng, self.numrngs, self.ions, self.numions = self.readORNLrng(rng_fn)

    def readORNLrng(self, fn):
        r = np.genfromtxt(fn)
        print r

    # reading in ORNL rng file
    def oldreadrng(self, fn):
        with open(fn, 'r') as file:
            r = [v.split() for v in file]
        numions = float(r[0][0])
        numrngs = float(r[0][1])
        end = int((1+numions)*2)
        # shortname + colour (3 floats)
        ions = r[2:end:2]
        rngs = r[int(end):int(end+numrngs)] # ranges
        rng = [[conv(col) for col in row] for row in rngs]
        return rng, numrngs, ions, numions

