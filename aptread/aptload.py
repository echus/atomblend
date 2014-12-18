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
            self.pos = pl.POS(pospath)
        except pl.ReadError:
            raise APTReadError('Error opening pos file %s' % pospath)
            return
        try:
            self.rng = rl.ORNLRNG(rngpath)
        except rl.ReadError:
            raise APTReadError('Error opening rng file %s' % rngpath)
            return

        # Range all points in posfile
        self.rng.loadpos(self.pos)
