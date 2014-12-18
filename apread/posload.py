# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   posload.py
# Date:   2014-07-01
# Author: Varvara Efremova
#
# Description:
# POS data loader classes
# =============================================================================

import numpy as np

class ReadError(Exception): pass

class POSInterface():
    xyz = None #: n x 3 numpy array of xyz points in input posfile
    mc  = None #: n x 1 numpy array of mass-to-charge ratios corresponding to all points

    def __len__(self):
        """Number of points in pos file"""
        return

class POS():
    """.pos file loader"""

    def __init__(self, pospath):
        data = self._parsefile(pospath)

        self._n  = data[0]
        self.xyz = data[1] #: n x 3 numpy array of xyz points in pos file
        self.mc  = data[2] #: n x 1 numpy array of corresponding mass-to-charge ratios

    # TODO more informative errors
    # TODO check it's actually a pos file
    def _parsefile(self, path: str) -> (int, np.ndarray, np.ndarray):
        """Parse input pos file"""
        try:
            with open(path, 'rb') as content_file:
                pos_raw = content_file.read()
        except (IOError, FileNotFoundError):
            raise ReadError('Error opening pos file %s' % path)
            return

        pos_array = np.ndarray((len(pos_raw)/4,), dtype='>f', buffer=pos_raw)
        pos = np.reshape(pos_array, (-1, 4))
        npoints = len(pos)
        xyz = pos[:,0:3]
        mc = pos[:,3]
        return npoints, xyz, mc

    def __len__(self):
        """Return number of points in pos file"""
        return self._n
