#!/usr/bin/env python

import numpy as np
from aptread.aptload import APData

pospath = "./data/R04.pos"
rngpath = "./data/R04.rng"

data = APData(pospath, rngpath)
print(data.xyz)
