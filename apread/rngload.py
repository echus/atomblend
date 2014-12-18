# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   rngload.py
# Date:   2014-07-01
# Author: Varvara Efremova
#
# Description:
# Available range loader classes
# =============================================================================

import numpy as np

class ReadError(Exception): pass

class ORNLRNG():
    """
    ORNL range file loader

    Usage::

      range = ORNLRNG("/path/to/file.rng") # Loads and parses rangefile
      range.loadpos(posloader_object)      # Ranges posfile

      range.atomlist                       # List of all atoms ranged
      range.getatom("Si")                  # Returns a list of loaded pos
                                           # points matching ion "Si"
    """
    def __init__(self, rngpath):
        # Load raw rangefile information
        self._rawdata = self._parsefile(rngpath)

        self.natoms  = self._rawdata['natoms']
        self.nranges = self._rawdata['nranges']

        # Internal use range/atom/ion structures
        self._ranges = None #: Internal range list (np.ndarray shape (2,nranges))
        self._atoms  = None #: Internal atom dictionary (atom name -> range indices)
        self._ions   = None #: Internal ion dictionary (ion name -> range indices)

        # Public range information
        self.rangelist = None #: List of range index references available
        self.atomlist  = None #: List of atom names (str)
        self.ionlist   = None #: List of ion names (str)

        # Populate range information
        self._genranges()
        self._genions()
        self._genatoms()

        # Initialise loadable pos information (used by loadpos)
        self._pos    = None #: Linked pos object reference
        self._posmap = None #: Array mapping pos points to ranges (1:1)



    # === RNG file parser ===
    def _parsefile(self, rngpath: str) -> dict:
        """
        Parse and return input rangefile as dict

        Arguments:

        * **rngpath** - Path to range file

        Returns:

        * **ranges** - nranges x 2 array of floats of defined ranges in rng
        * **atoms** - natoms x 2 array of atom shortnames and colours
        * **composition** - Boolean ion composition array (nranges x natoms)
        * **natoms, nragnes** - Number of atoms and ranges in rngfile
        """

        # TODO check it's a rng file (avoid utf-8 encoding errors)
        try:
            with open(rngpath, 'r') as file:
                r = [v.split() for v in file]
        except (IOError, FileNotFoundError):
            raise ReadError('Error opening rng file %s' % rngpath)
            return

        natoms = int(r[0][0])
        nranges = int(r[0][1])
        end = int((1+natoms)*2)

        # shortname + colour (3 floats)
        atoms = np.array(r[2:end:2])
        rngs = r[int(end):int(end+nranges)] # ranges

        # Read rows as numpy string array
        rngsconv = np.array(rngs, dtype='S10')

        ranges = rngsconv[:,1:3].astype('f8') # Extract ranges as
                                              # 2 col array of floats
        composition = rngsconv[:,3:3+natoms].astype('b') # Extract ion
                                                         # composition array
                                                         # as bool

        return {'ranges':ranges,
                'atoms':atoms,
                'comp':composition,
                'nranges':nranges,
                'natoms':natoms,
                }



    # === Range data processing functions ===
    def _genranges(self):
        # Generate internal and external range list structure
        # ===
        # Uses self._rawdata
        # Sets self._ranges, self.rangelist

        self._ranges   = self._rawdata['ranges']
        self.rangelist = range(len(self._ranges))

    def _genatoms(self):
        # Generate atoms dictionary relating human-readable atom ID strings
        # to corresponding range indices
        # ===
        # Uses self._rawdata
        # Sets self._atoms, self.atomlist
        # ===
        # atoms    : atom ID -> rnginds dictionary
        # atomlist : ordered list of atom IDs
        #            (corresponding to _rawdata['comp'] layout)

        atomnames = self._rawdata['atoms'][:,0]
        atoms = {}

        for i, atomname in enumerate(atomnames):
            # Range indexes of atom
            rnginds = self._rawdata['comp'][:,i].nonzero()[0]
            atoms[atomname] = rnginds

        self._atoms   = atoms
        self.atomlist = atomnames

    def _genions(self):
        # Generate ions dictionary relating human-readable ion ID strings
        # to corresponding range indices
        # ===
        # Uses self._rawdata
        # Sets self._ions, self.ionlist
        # ===
        # ions    : ion ID -> rnginds dictionary
        # ionlist : ordered list of ion IDs (corresponding to rngcomp layout)

        # Unique ions in omposition array from .rng file
        boolcomp = self._rawdata['comp'].astype(bool)
        ionscomp = _unique_rows(boolcomp)

        ions = {} # Ions string ID -> range index dictionary
        ionnames = []

        # Gen list of rnglist indices corresponding to the unique ions
        for ion in ionscomp:
            # rnginds: all indices in self._ranges corresponding to current ion
            rnginds = np.where((boolcomp == ion).all(axis=1))[0]

            # Get list of atom names in ion
            atomnames = self._rawdata['atoms'][:,0]
            atoms = atomnames[ion]
            # Concat atom names -> ion name string
            ionname = "".join(atoms)

            ions[ionname] = rnginds
            ionnames.append(ionname)

            print("ION", ion)
            print("IONNAME", ions[ionname])
            print()

        self._ions   = ions
        self.ionlist = ionnames



    # === POS ranging functions ===
    def loadpos(self, pos):
        """Link new pos object to range file"""
        # Sets self._pos, self._posmap

        self._pos = pos
        self._genposmap() # Map range information to loaded pos info

    def _genposmap(self):
        """
        Map pos information to associated ranges in self._posmap

        | Called by: self.loadpos()
        | Requires: self._pos
        | Sets: self._posmap
        """
        mc = self._pos.mc

        rngmap = np.zeros(mc.shape)
        for rngind, rng in enumerate(self._ranges):
            rng = self._ranges[rngind,:]
            # rngarray: 1 where mc matches current range, 0 where not
            rngarray = ((mc > rng[0]) & (mc < rng[1])).astype(int)
            rngarray *= (rngind + 1) # add one to differentiate between 0 indeces and
                                     # unranged points
            rngmap += rngarray

        self._posmap = rngmap



    # === POS point return functions ===
    # TODO find a cleaner way to vectorize this?
    def getrange(self, rnginds: 'int or list of ints') -> np.ndarray:
        """
        Returns all xyz points matching the selected range reference(s).

        Arguments:

        * **rnginds** - indexes of wanted range in self.ranges (int or array_like)
        * **mc** - array of mass to charge ratios to operate on
        """
        mc  = self._pos.mc
        xyz = self._pos.xyz

        # rnginds indexing starts from 1 internally
        # 0 points in rngmap are unranged points
        rnginds += 1
        ind = np.zeros(mc.shape, dtype=bool)
        if isinstance(rnginds, int):
            ind = (self._posmap == rnginds)
        elif isinstance(rnginds, list) or isinstance(rnginds, np.ndarray):
            for ri in rnginds:
                ind = np.logical_xor(ind, (self._posmap == ri))
        else:
            raise InvalidRngError('APTloader.getrange input "rnginds" is not a valid int or list')
            return None

        return xyz[ind]

    def getion(self, ionname: str) -> np.ndarray:
        """ Returns all points that match the selected ion.

        Arguments:

        * **ionname** - Ion name reference in ionlist
        """
        mc  = self._pos.mc
        xyz = self._pos.xyz

        rnginds = self._ions[ionname]
        return self.getrange(rnginds)

    def getatom(self, atomname: str) -> np.ndarray:
        """ Returns all points that match the selected atom.

        Arguments:

        * **atomname** - Atom name reference in atomlist
        """
        mc  = self._pos.mc
        xyz = self._pos.xyz

        rnginds = self._atoms[atomname]
        return self.getrange(rnginds)



# === Helper functions ===
def _unique_rows(a):
    # Helper function: returns unique rows in np 2d array
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))
