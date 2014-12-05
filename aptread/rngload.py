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

class ReadError(Exception): pass

# === Rangefile loader interface definition ===
class RangeLoader():
    """
    Abstract interface definition for rangefile loader classes
    Each rangefile loader must implement these functions
    """

    def __init__(self, path):
        self.loadfile(path)

    def loadfile(self, path):
        return

    def getatoms(self, mc):
        return

    def getion(self, mc):
        return

    def getisotope(self, mc):
        return

    def getcolour(self, atomname):
        return

    def atomlist(self):
        return

    def ionlist(self):
        return

    def rnglist(self):
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
        return


    def atomlist(self):
        """Return list of all atoms in rangefile"""
        atomlist = list(self.colours.keys())
        return atomlist

    def ionlist(self):
        """Return list of all ions in rangefile"""
        ions = []
        for line in self.ranges:
            atoms = line[1]
            ions.append(atoms)

        # Remove duplicates
        ionlist = list(set(ions))

        return ionlist

    def rnglist(self):
        """Return list of all ranges in rangefile"""
        # NOTE currently a list of range tuples
        # referenced by "rngid" = index in list
        # There is possibly a better way to do this

        rnglist = []
        for line in self.ranges:
            rnglist.append(line[0])
        return rnglist



    def getatoms(self, mc):
        """
        Returns tuple of atoms matching the given m/c.
        Returns None for an unranged m/c.
        """

        # Note: assumes there are no overlapping ranges
        # This should be checked upon loading the range file
        for rng, atoms in self.ranges:
            if (mc > rng[0]) & (mc < rng[1]):
                return atoms
        return None

    def getion(self, mc):
        """
        Returns ion name matching the given m/c.
        Returns None for an unranged m/c.
        """

        for rng, atoms in self.ranges:
            if (mc > rng[0]) & (mc < rng[1]):
                return "".join(atoms)
        return None

    def getisotope(self, mc):
        """Return isotope matching the given m/c"""
        # TODO
        return

    def getcolour(self, atomname):
        return self.colours[atomname]



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

        Input:
        rngs      : 2 column array of ranges (min, max)
        atomsraw  : 4 column array of atoms (name, R, G, B)
        rngcomp   : composition array

        Returns:
        rangedict : (min m/c, max m/c) -> (matching atoms)
        atomdict  : (str) atom name -> (R, G, B) atom colour
        """
        ranges = []
        atoms = {}

        # Populate rangedict
        for i, rng in enumerate(rngsraw):
            comp = rngcomp[i]                   # Range composition

            atominds = np.nonzero(comp)[0]      # Inds of atoms in range
            rngatoms = atomsraw[atominds,0]        # Atoms in range with colours

            rangetuple = (tuple(rng), tuple(rngatoms))
            ranges.append(rangetuple)

        # Populate atomdict
        for atom in atomsraw:
            atoms[atom[0]] = (atom[1], atom[2], atom[3])

        print(ranges)
        print(atoms)
        return ranges, atoms



# Helper functions
def _unique_rows(a):
    # Returns unique rows in numpy 2D array
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))
