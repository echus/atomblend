#!/usr/bin/env python
# APTloader.py
# ReferenceImplementationPython
#
# Author: Varvara Efremova
# Date: 14 April 2014
# Copyright (c) 2014 Australian Centre for Microscopy & Microanalysis (ACMM), The University of Sydney, NSW 2006 Australia. All rights reserved.

# TODO: chage "rngatoms", "ions" to something that makes sense
# rngatoms: sparse array of composition of particular range
# ions: total atoms present


import numpy as np

# TODO this only works when run from inside blender/outside package
# - what's a better way of referencing modules within a package?
import POSloader as pl
import ORNLRNGloader as rl

class APTReadError(Exception): pass

# read in complete pos + rng info
class ReadAptData():
    def __init__(self, pos_fn, rng_fn):
        try:
            self._posfile = pl.ReadPos(pos_fn)
        except pl.ReadError:
            raise APTReadError('Error opening pos file %s' % pos_fn)
            return
        try:
            self._rngfile = rl.ReadRng(rng_fn)
        except rl.ReadError:
            raise APTReadError('Error opening rng file %s' % rng_fn)
            return

        self.numpts = self._posfile.numpts
        self.cm = self._posfile.cm
        self.xyz = self._posfile.xyz
        self.rng = self._rngfile.rng
        self.rngcomp = self._rngfile.rngcomp
        self.atominfo = self._rngfile.atominfo
        # TODO change self.listatoms to atomlist (name), & change in blender
        self.listatoms = list(self.atominfo[:,0])

        # --- SLOW LOOP HERE ---
        # populate array of info about atoms
        self.info = np.zeros((self.numpts, 4), dtype="|S3")
        print "APTloader init - total points to load:", self.numpts
        allpts = range(0, self.numpts)
        # TODO efficient way to load info into memory?? apply info to all points??

        percent = self.numpts/100
        for i in range(0, self.numpts):



            if not i%percent:
                #if i/float(self.numpts) >= 0.02:
                #    break
                print "%.2f\n" % (i/float(self.numpts)*100.0)
            indinfo = self._getinfo(i)
            self.info[i] = self._getinfo(i)

    # returns nx4 array of information of atoms matching c/m ratio of posfile point i
    # [atom name eg 'Al', R, G, B]
    def _getinfo(self, i):
        # TODO check that i isn't out of bounds
        cm = self.cm[i]
        # MAYBE??
        #self.rng[:,0] == lower range list
        # add cm to end of it (append in numpy?)
        # sort
        # get new index of cm?
        # then index-1 is the lower bound
        # check index-1 higher bound: if > i then


        compind = np.where((self.rng[:,0] < cm) & (self.rng[:,1] > cm))
        compind = compind[0]
        if len(compind) == 0:
            # no matching range found
            return None

        # TODO check in rngloader that no ranges overlap and throw InvalidRngError

        # this is the raw atomic composition array (sparse) for selected rng
        rawcomp = self.rngcomp[compind][0]
        # get indices of composition atoms in rngfile.atominfo array
        indatominfo = np.where(rawcomp == True)
        comp = self.atominfo[indatominfo][0]

        if comp is None:
            return self._rngfile.null_atom
        return comp

    # returns atom information associated with the given c/m ratio
    def _getatom(self, cm):
        # find index where lower rng < cm < higher rng
        # np.where returns tuple
        # TODO throw error if tuple length received > 1: means cm  matched multiple ranges
        compind = np.where((self.rng[:,0] < cm) & (self.rng[:,1] > cm))
        compind = compind[0]
        if len(compind) == 0:
            # no matching range found
            return None

        # TODO check in rngloader that no ranges overlap and throw InvalidRngError

        # this is the raw atomic composition array (sparse) for selected rng
        rawcomp = self.rngcomp[compind][0]
        # get indices of composition atoms in rngfile.atominfo array
        indatominfo = np.where(rawcomp == True)
        comp = self.atominfo[indatominfo][0]
        return comp

    # get indexes of all points matching specified atom
    def getpoints(self, atom):
        # get info for each point - nx4 array
        ind = range(0, self.numpts-1)
        func = self.getinfo
        vgetinfo = np.vectorize(func)
        return vgetinfo
