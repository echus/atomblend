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
# Sample header to use in AtomBlend projects.
# =============================================================================

import numpy as np

# Default null_atom value
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

    def __init__(self, rng_path, null_atom=NULL_ATOM):
        # Read rng file info
        self.loadfile(rng_path)

        # Set default null_atom value (to be returned for any atoms
        # that don't match ranges in the rngfile)
        self.null_atom = null_atom

        # TODO add function that returns atominfo shape (eg 1x4)

    # TODO check it's a rng file (avoid utf-8 encoding errors)
    def loadfile(self, path):
        """Reads and returns parsed rng file"""

        try:
            with open(path, 'r') as file:
                r = [v.split() for v in file]
        except (IOError, FileNotFoundError):
            raise ReadError('Error opening rng file %s' % path)
            return

        # Data pre-processing
        natoms, nrngs, rngs, atominfo, rngcomp = self._read(r)
        self.natoms, self.nrngs = natoms, nrngs

        # Parse raw rng data into dicts
        self.rangedict, self.atomdict = self._parse(rngs, atominfo, rngcomp)
        return

    def _read(self, r):
        """ Read range data from file

        Input:
        r        : raw split() file input

        Output:
        natoms   : number of atoms
        nrngs    : number of ranges
        rngs     : 2 column array of ranges (min, max)
        atominfo : 4 column array of atoms (name, R, G, B)
        rngcomp  : composition array
        """

        natoms = int(r[0][0])         # Total number of atoms
        nrngs  = int(r[0][1])          # Total number of rngs

        endrow = int((1+natoms)*2)    # rngfile end row

        # Extract raw rng data
        atominfo = np.array(r[2:endrow:2])        # All atom shortnames and
                                                  # colours
                                                  # Columns [name, R, G, B]

        rawrngs = r[int(endrow):int(endrow+nrngs)] # Raw ranges
        rngsconv = np.array(rawrngs, dtype='S10') # Rows as numpy strings

        rngs = rngsconv[:,1:3].astype('f8') # Extract ranges
        rngcomp = rngsconv[:,3:3+natoms].astype('b') # Extract array of atoms in range

        return natoms, nrngs, rngs, atominfo, rngcomp


    def _parse(self, rngs, atominfo, rngcomp):
        """ Parse raw range data into dicts

        Input:
        rngs      : 2 column array of ranges (min, max)
        atominfo  : 4 column array of atoms (name, R, G, B)
        rngcomp   : composition array

        Returns:
        rangedict : (min m/c, max m/c) -> (matching atoms)
        atomdict  : (str) atom name -> (R, G, B) atom colour
        """
        rangedict = {}
        atomdict = {}

        # Populate rangedict
        for i, rng in enumerate(rngs):
            comp = rngcomp[i]                   # Range composition

            atominds = np.nonzero(comp)[0]      # Inds of atoms in range
            atoms = atominfo[atominds,0]        # Atoms in range with colours

            rangedict[tuple(rng)] = tuple(atoms)

        # Populate atomdict
        for atom in atominfo:
            atomdict[atom[0]] = (atom[1], atom[2], atom[3])

        print(rangedict)
        print(atomdict)
        return rangedict, atomdict



# Helper functions
def _unique_rows(a):
    # Returns unique rows in numpy 2D array
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))


