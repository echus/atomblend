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
        self.natoms = None
        self.nranges = None

        self.atomlist = None
        self.ionlist = None
        self.rnglist = None

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
        ions = self.ranges['atoms']
        ionlist = np.unique(ions)
        return ionlist

    def _genrnglist(self):
        """Return list of all ranges in rangefile"""
        rngl = self.ranges['mcl']
        rngu = self.ranges['mcu']

        # Can't simply view self.ranges[['mcl', 'mcu']]
        # due to object field in self.ranges atoms column
        rnglist = np.column_stack((rngl, rngu))
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

        (Assumes no ranges overlap)
        """
        # TODO raise error if test mc matches more than one range

        match = (mc > self.ranges['mcl']) & (mc < self.ranges['mcu'])
        if match.any():
            ion = self.ranges['atoms'][match][0]
            return ion
        else:
            return None

        #    if (mc > rng[0]) & (mc < rng[1]):
        return None

    def getrng(self, mc):
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
        rngsraw   : 2 column array of ranges (min, max)
        atomsraw  : 4 column array of atoms (name, R, G, B)
        rngcomp   : composition array

        Returns:
        ranges : [(min m/c, max m/c), (matching atoms)] (nrngs x 2 np array)
        atoms  : (str) atom name -> (R, G, B) atom colour (natoms x dict)
        """
        ranges_dtype = np.dtype([('mcl', np.float32), ('mcu', np.float32), ('atoms', np.object)])
        ranges = np.zeros(self.nrngs, dtype=ranges_dtype)
        atoms = {}

        # Populate ranges
        for i, rng in enumerate(rngsraw):
            comp = rngcomp[i]                   # Range composition

            atominds = np.nonzero(comp)[0]      # Inds of atoms in range
            rngatoms = atomsraw[atominds,0]     # Atoms in range with colours

            ranges[i]['mcl'] = rng[0]
            ranges[i]['mcu'] = rng[1]
            ranges[i]['atoms'] = tuple(rngatoms)

        # Populate atoms dict
        for atom in atomsraw:
            atoms[atom[0]] = (atom[1], atom[2], atom[3])


        print("RANGES GEN'D", ranges)
        return ranges, atoms



# Helper functions
def _unique_rows(a):
    # Returns unique rows in numpy 2D array
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))
