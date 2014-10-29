# POSloader.py
# ReferenceImplementationPython
#
# Author: Anna Ceguerra
# Date: 4 March 2013
# Copyright (c) 2013 Australian Centre for Microscopy & Microanalysis (ACMM), The University of Sydney, NSW 2006 Australia. All rights reserved.

import numpy as np
class ReadError(Exception): pass

class ReadPos():
    def __init__(self, pos_fn):
        self.numpts, self.xyz, self.mc = self.loadfile(pos_fn)

    # read in pos file
    # TODO more informative errors
    # TODO check it's actually a pos file
    def loadfile(self, fn):
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
        return numpoints, xyz, mc
