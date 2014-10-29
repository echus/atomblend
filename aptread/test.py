#!/usr/bin/env python

from APTloader import *

try:
    data = ReadAptData("blah", "al.rng")
except APTReadError, e:
    print "Error!"
