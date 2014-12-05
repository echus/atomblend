# test-ORNLRNGloader.py

import os.path

from rngload import RNG

PATH = "../data/test.rng"

path = os.path.abspath(PATH)

rngfile = RNG(path)
#print "ranges:", rngfile.rng
#print "range atoms/rngcomp:", rngfile.rngcomp
#print "ions/atominfo:", rngfile.atominfo
print("n ions/numatoms:", rngfile.natoms)
print("n ranges:", rngfile.nrngs)
print("m/c=1 atoms:", rngfile.getatoms(1))
print("m/c=14 atoms:", rngfile.getatoms(14))
print("m/c=0.1 atoms:", rngfile.getatoms(0.1))
print("m/c=1 ion:", rngfile.getion(1))
print("m/c=14 ion:", rngfile.getion(14))
print("m/c=0.1 ion:", rngfile.getion(0.1))
print()
print("atomlist", rngfile.atomlist)
print("ionlist", rngfile.ionlist)
print("rnglist", rngfile.rnglist)
