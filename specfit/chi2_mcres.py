#! /usr/bin/env python

'''
	Take a series os spectra (*.spres.npy) resulting from specfitMC.py, calculate and plot chi_square.
'''

import os,sys
import numpy as np
import pylab as py
import logging as log
#import pymc
from astropy.table import Table


################################################################################

def main(argv):

	log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
					level=log.DEBUG)

	from optparse import OptionParser
	
	parser = OptionParser()
	
	parser.add_option('-o','--output',
					  help = 'Name of output file.'
					  ,type='string')
	parser.add_option('-v','--verbose',
					  help = 'Run in verbose mode.',action='store_true',
					  default=False)

	opt,args = parser.parse_args(argv)

	chi2 = np.zeros(len(args[1:]))
	
	for i,spec in enumerate(args[1:]):
		log.debug('Reading %s'%spec)
		sp = np.load(spec)
		chi2[i] = np.mean( (sp['data'] - sp['model'])**2. / sp['model'] )

	ibest = chi2.argmin()
	iworst = chi2.argmax()
	best=args[1:][chi2.argmin()]
	worst=args[1:][chi2.argmax()]

	print best, chi2[ibest]
	print worst, chi2[iworst]

	py.hist(chi2,bins=100)

	py.figure(2)

	py.subplot(211)

	sp = np.load(args[1:][ibest])

	py.plot(sp['wave'],sp['data'])
	py.plot(sp['wave'],sp['model'])

	py.subplot(212)
	
	sp = np.load(args[1:][iworst])
	
	py.plot(sp['wave'],sp['data'])
	py.plot(sp['wave'],sp['model'])

	py.show()

	return 0

################################################################################


if __name__ == "__main__":

	main(sys.argv)

################################################################################