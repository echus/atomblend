from rngload import ORNLRNG

path = "../data/R04.rng"

rngfile = ORNLRNG(path)
print("Ranges:", rngfile.rangelist)
print("Atoms: ", rngfile.atomlist)
print("Ions:  ", rngfile.ionlist)
print("n ranges:", rngfile.nranges)
print("n atoms:",  rngfile.natoms)
