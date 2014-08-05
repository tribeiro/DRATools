#! /usr/bin/env

'''
	Cut spectrum (stored as .npy files).
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
	parser.add_option('--wmin',
					  help = 'Minimum wavelenght.'
					  ,type=float)
	parser.add_option('--wmax',
					  help = 'Maximum wavelenght.'
					  ,type=float)

	opt,args = parser.parse_args(argv)

	if opt.verbose:
		log.basicConfig(level=log.INFO)

	for fname in args[1:]:
		sp = np.load(fname)

		mask = np.zeros(len(sp[0])) == 0
		if opt.wmin:
			mask = np.bitwise_and(mask,sp[0] > opt.wmin)
		if opt.wmax:
			mask = np.bitwise_and(mask,sp[0] < opt.wmax)

		rsp = np.array([sp[0][mask],sp[1][mask]])

		ofile = 'c_'+fname

		log.info('%s -> %s'%(fname,ofile))
		np.save(ofile,rsp)

	return 0

if __name__ == '__main__':

	main(sys.argv)
