#! /usr/bin/env

'''
Convert dk files to numpy.
'''

import sys,os
import numpy as np
import logging
from StringIO import StringIO

import pylab as py

def readdk(filename):

	fp = open(filename,'r')
	
	data = fp.readlines()
	
	end = 'END     \n'
	
	istart = data.index(end)
	
	d = StringIO(data[istart])
	for i in range(istart+1,len(data)):
		d.write(data[i])

	d.seek(0)
	return np.loadtxt(d,unpack=True)

def main(argv):

	logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',level=logging.DEBUG)

	from optparse import OptionParser
	
	parser = OptionParser()
	parser.add_option('-v','--verbose',
		  help = 'Run in verbose mode.',action='store_true',default=False)

	opt,args = parser.parse_args(argv)

	if opt.verbose:
		logging.basicConfig(level=logging.INFO)

	for fname in args[1:]:
		rsp = readdk(fname)
		
		ofile = fname.replace('.dk','.npy')
		logging.info('%s -> %s'%(fname,ofile))

		#py.plot(rsp[0],rsp[1])
		#py.show()

		np.save(ofile,rsp)

	return 0

if __name__ == '__main__':

	main(sys.argv)
