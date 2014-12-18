# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   aptload.py
# Date:   2014-07-01
# Author: Varvara Efremova
#
# Description:
# APT data loader
# =============================================================================

import numpy as np

from . import POSloader as pl
from . import ORNLRNGloader as rl

# === Helper functions ===
def _unique_rows(a):
    # Helper function: returns unique rows in np 2d array
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

# === Exceptions ===
class APTReadError(Exception): pass
class InvalidRngError(Exception): pass
class InvalidIndexError(Exception): pass

# === Class defs ===
class APData():
    """
    APT data reader class
    """
    def __init__(self, pospath, rngpath):
        try:
            self._posfile = pl.ReadPos(pospath)
        except pl.ReadError:
            raise APTReadError('Error opening pos file %s' % pospath)
            return
        try:
            self._rngfile = rl.ReadRng(rngpath)
        except rl.ReadError:
            raise APTReadError('Error opening rng file %s' % rngpath)
            return

        self.numpts = self._posfile.numpts
        self.mc = self._posfile.mc
        self.xyz = self._posfile.xyz

        self.rngcomp = self._rngfile.rngcomp
        self.atominfo = self._rngfile.atominfo

        self.ranges = self._rngfile.rng

        self.atoms, self.atomlist = self.genatoms()
        self.ions, self.ionlist  = self.genions()
        print(self.atoms, self.atomlist)
        print(self.ions, self.ionlist)

        # Generate array mapping points to ranges
        self.rngmap = self.genrngmap(self.mc)



    # === Generation functions ===
    def genrngmap(self, mc):
        """
        Calculate array mapping array of mcs to their respective ranges
        """
        rngmap = np.zeros(mc.shape)

        for rngind, rng in enumerate(self.ranges):
            rng = self.ranges[rngind,:]
            # rngarray: 1 where mc matches current range, 0 where not
            rngarray = ((mc > rng[0]) & (mc < rng[1])).astype(int)
            rngarray *= (rngind + 1) # add one to differentiate between 0 indeces and
                                     # unranged points
            rngmap += rngarray

        return rngmap

    def genatoms(self):
        """
        Generate atoms dictionary relating human-readable atom ID strings
        to corresponding range indices

        Outputs:
        atoms: atom ID -> rnginds dictionary
        atomnames: ordered list of atom IDs (corresponding to rngcomp layout)
        """

        atomnames = self._rngfile.atominfo[:,0]
        atoms = {}

        for i, atomname in enumerate(atomnames):
            rnginds = self.rngcomp[:,i].nonzero()[0] # Range indexes of atom
            atoms[atomname] = rnginds

        return atoms, atomnames

    def genions(self):
        """
        Generate ions dictionary relating human-readable ion ID strings
        to corresponding range indices

        ions:     ion ID -> rnginds dictionary
        ionnames: ordered list of ion IDs (corresponding to rngcomp layout)
        """
        # Unique ions in omposition array from .rng file
        boolcomp = self.rngcomp.astype(bool)
        ionscomp = _unique_rows(boolcomp)

        ions = {} # Ions string ID -> range index dictionary
        ionnames = []

        # Gen list of rnglist indices corresponding to the unique ions
        for ion in ionscomp:
            # rnginds: all indices in rnglist/rngcomp corresponding to current ion
            rnginds = np.where((boolcomp == ion).all(axis=1))[0]

            atoms = self.atomlist[ion] # List of atom names in ion
            ionname = "".join(atoms)   # String ion name (cat of atoms)

            ions[ionname] = rnginds
            ionnames.append(ionname)

            print("ION", ion)
            print("IONNAME", ions[ionname])
            print()

        return ions, ionnames



    # === API functions ===
    # TODO find a cleaner way to vectorize this?
    def getrng(self, rnginds, mc, xyz):
        """
        Returns all xyz points in the selected range reference(s).

        Arguments:
        rnginds -- indexes of wanted range in self.ranges (int or array_like)
        mc     -- array of mass to charge ratios to operate on

        Returns:
        Numpy 2D array of xyz points matching the selected range(s)
        """
        # rnginds indexing starts from 1 internally
        # 0 points in rngmap are unranged points
        rnginds += 1
        ind = np.zeros(mc.shape, dtype=bool)
        if isinstance(rnginds, int):
            ind = (self.rngmap == rnginds)
        elif isinstance(rnginds, list) or isinstance(rnginds, np.ndarray):
            for ri in rnginds:
                ind = np.logical_xor(ind, (self.rngmap == ri))
        else:
            raise InvalidRngError('APTloader.getrng input "rnginds" is not a valid int or list')
            return None

        return xyz[ind]

    def getion(self, ionname, mc, xyz):
        """ Returns all points that match the selected ion.

        Arguments:
        ionind -- index of the ion in self.ionlist
        """

        rnginds = self.ions[ionname]
        return self.getrng(rngind, mc, xyz)

    def getatom(self, atomname, mc, xyz):
        """ Returns all points that match the selected atom.

        Arguments:
        atomind -- index of the atom in self.atomlist
        """
        rnginds = self.atoms[atomname]
        return self.getrng(rngind, mc, xyz)
