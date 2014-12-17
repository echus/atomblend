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
# Rangefile loader definitions
# =============================================================================

import numpy as np
from operator import itemgetter # For sorting dict keys

from .betweendict import BetweenDict

class ReadError(Exception): pass

# === Rangefile loader interface definition ===
class RangeLoader():
    """
    Abstract interface definition for rangefile loader classes
    Each rangefile loader must implement these functions
    """

    def __init__(self, path):
        self.natoms = None
        self.nranges = None

        self.atomlist = None
        self.ionlist = None
        self.rnglist = None

        self.loadfile(path)

    def loadfile(self, path):
        return

    def atoms(self, mc):
        return

    def rangeid(self, mc):
        return

    def colour(self, atomname):
        return


# === Concrete rangefile loader classes ===
class RNG(RangeLoader):
    """.rng loader definition"""

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
        natoms, nrngs, rngsraw, atomsraw, rngcomp = self._read(r)
        self.natoms, self.nrngs = natoms, nrngs

        # Parse raw rng data into lists
        self.ranges, self.colours = self._parse(rngsraw, atomsraw, rngcomp)

        # Generate atom, ion, rng lists
        self.atomlist = self._genatomlist()
        self.ionlist = self._genionlist()
        self.rnglist = self._genrnglist()
        return


    def _genatomlist(self):
        """Return list of all atoms in rangefile"""
        atomlist = list(self.colours.keys())
        return atomlist

    def _genionlist(self):
        """Return list of all ions in rangefile"""
        ions = []
        for rng, rngdict in self.ranges.items():
            ions.append(rngdict['atoms'])

        ionlist = np.unique(ions)
        return ionlist

    def _genrnglist(self):
        """Return list of all ranges in rangefile"""
        # TODO sort these by range id
        return list(self.ranges.keys())



    def atoms(self, mc):
        """
        Returns tuple of atoms matching the given m/c.
        Returns None for an unranged m/c.
        """
        if mc in self.ranges:
            return self.ranges[mc]['atoms']
        else:
            return None

    def rangeid(self, mc):
        """Return isotope matching the given m/c"""
        # TODO
        if mc in self.ranges:
            return self.ranges[mc]['id']
        else:
            # return -1 for numpy int32 field convenience (used in aptload)
            return -1

    def colour(self, atomname):
        if atomname in self.colours:
            return self.colours[atomname]
        else:
            return None



    def _read(self, r):
        """ Read range data from file

        Input:
        r        : raw split() file input

        Output:
        natoms   : number of atoms
        nrngs    : number of ranges
        rngs     : 2 column array of ranges (min, max)
        atomsraw : 4 column array of atoms (name, R, G, B)
        rngcomp  : composition array
        """

        natoms = int(r[0][0])         # Total number of atoms
        nrngs  = int(r[0][1])          # Total number of rngs

        endrow = int((1+natoms)*2)    # rngfile end row

        # Extract raw rng data
        atomsraw = np.array(r[2:endrow:2])        # All atom shortnames and
                                                  # colours
                                                  # Columns [name, R, G, B]

        rngslist = r[int(endrow):int(endrow+nrngs)] # Raw ranges
        rngsconv = np.array(rngslist, dtype='S10') # Rows as numpy strings

        rngsraw = rngsconv[:,1:3].astype('f8') # Extract ranges
        rngcomp = rngsconv[:,3:3+natoms].astype('b') # Extract array of atoms in range

        return natoms, nrngs, rngsraw, atomsraw, rngcomp


    def _parse(self, rngsraw, atomsraw, rngcomp):
        """ Parse raw range data into dicts
        Run after self._read()

        Input:
        rngsraw   : 2 column array of ranges (min, max)
        atomsraw  : 4 column array of atoms (name, R, G, B)
        rngcomp   : composition array

        Returns:
        ranges : (range [len=2]) mc range -> dict(atoms -> (tup), rngid -> int)
        atoms  : (str) atom name -> (R, G, B) atom colour (natoms x dict)
        """

        ranges = BetweenDict()
        colours = {}

        # Populate ranges
        for i, rng in enumerate(rngsraw):
            comp = rngcomp[i]                   # Range composition

            atominds = np.nonzero(comp)[0]      # Inds of atoms in range
            rngatoms = atomsraw[atominds,0]     # Atoms in range with colours

            rngdict = {}
            rngdict['id'] = i
            rngdict['atoms'] = tuple(rngatoms)

            ranges[list(rng)] = rngdict

        # Populate colours dict
        for atom in atomsraw:
            colours[atom[0]] = (atom[1], atom[2], atom[3])

        return ranges, colours
