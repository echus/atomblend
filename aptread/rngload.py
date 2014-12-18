# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   rngload.py
# Date:   2014-07-01
# Author: Varvara Efremova
#
# Description:
# Available range loader classes
# =============================================================================

import numpy as np

class ReadError(Exception): pass

class ORNLRNG():
    def __init__(self, rngpath):
        # read rng file info
        self.rng, self.rngcomp, self.numrngs, self.atominfo, self.numatoms = self.loadfile(rngpath)

    def loadfile(self, rngpath):
        # TODO check it's a rng file (avoid utf-8 encoding errors)
        try:
            with open(rngpath, 'r') as file:
                r = [v.split() for v in file]
        except (IOError, FileNotFoundError):
            raise ReadError('Error opening rng file %s' % rngpath)
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

