# ORNLRNGloader.py
# ReferenceImplementationPython
#
# Authors: Anna Ceguerra, Varvara Efremova
# Date: 14 April 2014
# Copyright (c) 2014 Australian Centre for Microscopy & Microanalysis (ACMM), The University of Sydney, NSW 2006 Australia. All rights reserved.

import numpy as np

# default null_atom value
NULL_ATOM = np.array(['', '', '', ''])

class ReadError(Exception): pass

class ReadRng():
    # constant index definitions
    rng_sym = 0
    rng_low = 1
    rng_high = 2
    ions_name = 0
    ions_r = 1
    ions_g = 2
    ions_b = 3

    def __init__(self, rng_fn, null_atom=NULL_ATOM):
        # read rng file info
        self.rng, self.rngcomp, self.numrngs, self.atominfo, self.numatoms = self.loadfile(rng_fn)

        # set default null_atom value (to be returned for any atoms
        # that don't match ranges in the rngfile)
        self.null_atom = null_atom

        # TODO add function that returns atominfo shape (eg 1x4)

    # reading in ORNL rng file
    # TODO check it's a rng file (avoid utf-8 encoding errors)
    def loadfile(self, fn):
        try:
            with open(fn, 'r') as file:
                r = [v.split() for v in file]
        except (IOError, FileNotFoundError):
            raise ReadError('Error opening rng file %s' % fn)
            return

        numions = int(r[0][0])
        numrngs = int(r[0][1])
        end = int((1+numions)*2)
        # shortname + colour (3 floats)
        ions = np.array(r[2:end:2])
        rngs = r[int(end):int(end+numrngs)] # ranges

        # read rows as np strings
        rngsconv = np.array(rngs, dtype='S10')

        # extract ranges as floats, ion composition as bool
        rng = rngsconv[:,1:3].astype('f8') # extract only range
        rngatoms = rngsconv[:,3:3+numions].astype('b') # extract array of atoms in range

        return rng, rngatoms, numrngs, ions, numions

