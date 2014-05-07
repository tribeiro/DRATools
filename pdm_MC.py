#! /usr/bin/env python

import sys,os
from pyraf import iraf
from optparse import OptionParser
import numpy as np

iraf.noao()
iraf.astut()

def main(argv):
			
	from optparse import OptionParser
	
	parser = OptionParser()
	
	parser.add_option(	'--dataset',
						help='List of files to run pdm on',
						type='string')

	opt,args = parser.parse_args(argv)


	flist = np.loadtxt(opt.dataset,dtype='S',unpack=True)

	for i,f in enumerate(flist):
		print 'Running pdm on %s...'%f
		iraf.pdm(	infiles=f,
					batchfile='pdm_res%04i.dat'%i)


if __name__ == '__main__':

	main(sys.argv)