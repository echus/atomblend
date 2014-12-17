# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   APTloader.py
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
class ReadAPTData():
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

        self.rnglist = self._rngfile.rng
        self.atomlist = self._rngfile.atominfo[:,0]
        self.ions = self.gen_ions()
        print(self.ions)

        # Generate array mapping points to ranges
        self.rngmap = self.gen_rngmap(self.mc)

    def gen_rngmap(self, mc):
        """
        Calculate array mapping array of mcs to their respective ranges
        """
        rngmap = np.zeros(mc.shape)

        for rngind, rng in enumerate(self.rnglist):
            rng = self.rnglist[rngind,:]
            # rngarray: 1 where mc matches current range, 0 where not
            rngarray = ((mc > rng[0]) & (mc < rng[1])).astype(int)
            rngarray *= (rngind + 1) # add one to differentiate between 0 indeces and
                                     # unranged points
            rngmap += rngarray

        return rngmap

    def gen_ions(self):
        """
        Generate ions dictionary relating human-readable ion ID strings
        to corresponding range indices
        """
        # Unique ions in omposition array from .rng file
        boolcomp = self.rngcomp.astype(bool)
        ionscomp = _unique_rows(boolcomp)

        ions = {} # Ions string ID -> range index dictionary

        # Gen list of rnglist indices corresponding to the unique ions
        for ion in ionscomp:
            # inds: all indices in rnglist/rngcomp corresponding to current ion
            inds = np.where((boolcomp == ion).all(axis=1))[0]

            atoms = self.atomlist[ion] # List of atom names in ion
            ionname = "".join(atoms)   # String ion name (cat of atoms)

            ions[ionname] = inds

            print("ION", ion)
            print("IONNAME", ions[ionname])
            print()

        return ions

    # TODO find a cleaner way to vectorize this?
    def getrng(self, rngind):
        """ Returns all xyz points in the selected range reference.

        Arguments:
        rngind -- index of the rng in self.rnglist (int or array_like)
                  value of -1 signifies unranged point

        Returns:
        numpy 2D array of xyz points
        """
        # rngind indexing starts from 1 internally
        # 0 points in rngmap are unranged points
        rngind += 1
        ind = np.zeros(self.mc.shape, dtype=bool)
        if isinstance(rngind, int):
            ind = (self.rngmap == rngind)
        elif isinstance(rngind, list) or isinstance(rngind, np.ndarray):
            for ri in rngind:
                ind = np.logical_xor(ind, (self.rngmap == ri))
        else:
            raise InvalidRngError('APTloader.getrng input "rngind" is not a valid int or list')
            return None
        return self.xyz[ind]

    def getion(self, ionind):
        """ Returns all points that match the selected ion.

        Arguments:
        ionind -- index of the ion in self.ionlist
        """
        ionref = self._ioninds[ionind] # get reference index to ion in rng array

        # select all ranges that match the given ion's compositions
        boolcomp = self.rngcomp.astype(bool)
        ion = boolcomp[ionref]

        # select rows in boolcomp that match ion
        # ie the ranges that match the ion composition
        # self.rngcomp[boolind] are the matching rng compositions
        boolind = (boolcomp == ion).all(axis=1)
        rngind = boolind.nonzero()[0]
        return self.getrng(rngind)

    # atomind indexing starts from 0
    # returns all points that match selected atom
    # calls:
    #   self.getrng
    def getatom(self, atomind):
        """ Returns all points that match the selected atom.

        Arguments:
        atomind -- index of the atom in self.atomlist
        """
        # TODO check for out of bounds atomind, throw error, or catch invalid index error?
        rngind = self.rngcomp[:,atomind].nonzero()[0]
        return self.getrng(rngind)
