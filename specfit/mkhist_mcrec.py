#!/usr/bin/env python

import sys,os
import numpy as np
import pylab as py

################################################################################

def main(argv):

	from optparse import OptionParser
	
	parser = OptionParser()
	
	parser.add_option('-f','--filename',
					  help = 'Input spectrum to fit.'
					  ,type='string')

	opt,args = parser.parse_args(argv)

	mcdata = np.load(opt.filename)
	
	for i,name in enumerate(mcdata.dtype.names[:-1]):
		py.subplot(5,2,i+1)
		py.hist(mcdata[name],weights=mcdata['chi2'].min()/mcdata['chi2'])

	py.show()

	return 0

################################################################################

if __name__ == '__main__':

	main(sys.argv)

################################################################################