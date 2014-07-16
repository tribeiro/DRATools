#! /usr/bin/env

'''
	Convert NextGen files to numpy.
'''

import sys,os
import numpy as np
import logging as log

def main(argv):

	log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
				level=log.DEBUG)

	from optparse import OptionParser

	parser = OptionParser()
	parser.add_option('-v','--verbose',
	help = 'Run in verbose mode.',action='store_true',default=False)

	opt,args = parser.parse_args(argv)

	if opt.verbose:
		log.basicConfig(level=log.INFO)

	for fname in args[1:]:
		sp = np.loadtxt(fname,unpack=True,usecols=(0,1),
						converters={0:lambda s: float(s.replace('D','e')),
									1:lambda s: float(s.replace('D','e'))})
		asort = sp[0].argsort()
		rsp = np.array([sp[0][asort],10**(sp[1][asort])+8.0])
		
		ofile = fname+'.npy'
		log.info('%s -> %s'%(fname,ofile))
		np.save(ofile,rsp)

	return 0

if __name__ == '__main__':

	main(sys.argv)
