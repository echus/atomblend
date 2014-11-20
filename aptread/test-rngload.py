# test-ORNLRNGloader.py

import os.path

from rngload import ReadRng

PATH = "../data/test.rng"

path = os.path.abspath(PATH)

rngfile = ReadRng(path)
#print "ranges:", rngfile.rng
#print "range atoms/rngcomp:", rngfile.rngcomp
#print "ions/atominfo:", rngfile.atominfo
print("n ions/numatoms:", rngfile.natoms)
print("n ranges:", rngfile.nrngs)
