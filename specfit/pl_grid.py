#! /usr/bin/env python

'''
	Given a list of template spectra grid, generate a plot with the grid
	parameters.
'''

import os,sys
import numpy as np
import pylab as py
import logging as log

################################################################################

def main(argv):

	log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
					level=log.INFO)

	from optparse import OptionParser
    
	parser = OptionParser()

	parser.add_option('-f','--filename',
						help = 'Input list with template spectra.'
						,type='string')

	opt,args = parser.parse_args(argv)

	data = np.loadtxt(opt.filename,dtype='S',unpack=True,ndmin=2)

	grid = np.array([ os.path.basename(d)[3:10] for d in data[0]]).T

	teff = np.array([t[:3] for t in grid],dtype=float)
	logg = np.array([t[3:] for t in grid],dtype=float)
	
	py.plot(teff,logg,'.')

	py.show()

################################################################################


if __name__ == "__main__":

	main(sys.argv)

################################################################################