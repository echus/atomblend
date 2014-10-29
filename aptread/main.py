#!/usr/bin/env python
import APTloader_test as al
import cProfile

cProfile.run("al.ReadAptData('al.pos','al.rng')")

