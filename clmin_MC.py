#! /usr/bin/env python

import sys,os
import pymc
from optparse import OptionParser
import pylab as py
import numpy as np

def main(argv):
	
	import clminF
	
	S = pymc.MCMC(clmin_root, db='pickle')
	S.sample(iter=10000, burn=5000, thin=2)

	print
	print 'root = ',S.root.value

	#py.figure(1)
	#py.subplot(131)
	py.hist(S.trace('root')[:])

	py.show()

if __name__ == '__main__':

	main(sys.argv)