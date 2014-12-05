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
# Posfile loader definition
# =============================================================================

import numpy as np

class ReadError(Exception): pass

class PosLoader():
    """
    Abstract XYZ pos loader definition:
    POS loaders must implement these functions
    """

    def __init__(self, path):
        self.npoints = None
        self.xyz     = None
        self.mc      = None

        self.loadfile(path)

    def loadfile(self, path):
        return



class POS(PosLoader):
    """.pos loader"""

    # TODO more informative errors
    # TODO check it's actually a pos file
    def loadfile(self, fn):
        """Read posfile at path fn"""
        try:
            with open(fn, 'rb') as content_file:
                pos_raw = content_file.read()
        except (IOError, FileNotFoundError):
            raise ReadError('Error opening pos file %s' % fn)
            return

        pos_array = np.ndarray((len(pos_raw)/4,), dtype='>f', buffer=pos_raw)
        pos = np.reshape(pos_array, (-1, 4))
        numpoints = len(pos)
        xyz = pos[:,0:3]
        mc = pos[:,3]

        self.npoints = numpoints
        self.xyz     = xyz
        self.mc      = mc
        return
