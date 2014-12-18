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

from . import posload as pl
from . import rngload as rl

# === Exceptions ===
class APReadError(Exception): pass
class InvalidRngError(Exception): pass
class InvalidIndexError(Exception): pass

# === Class defs ===
class APData():
    """
    APT data parsing class

    Usage::

        rngpath = "/path/to/rng"
        pospath = "/path/to/pos"
        data = APData(pospath, rngpath)

        data.pos                # Loaded posload object
        data.pos.xyz            # [x, y, z] array of all points in pos file

        data.rng                # Loaded rngload object
        data.rng.atomlist       # List of all atoms defined in rng file
        data.rng.getatom("Si")  # Return all points in pos file matching Si's range

    """
    def __init__(self, pospath, rngpath):
        try:
            self.pos = pl.POS(pospath)
        except pl.ReadError:
            raise APReadError('Error opening pos file %s' % pospath)
            return
        try:
            self.rng = rl.ORNLRNG(rngpath)
        except rl.ReadError:
            raise APReadError('Error opening rng file %s' % rngpath)
            return

        # Range all points in posfile
        self.rng.loadpos(self.pos)
