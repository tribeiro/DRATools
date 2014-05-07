#! /usr/bin/env python

import sys,os
import numpy as np
import pylab as py

######################################################################

def main(argv):

	from optparse import OptionParser
	
	parser = OptionParser()
	parser.add_option('-f','--file',
			  help = 'File with eclipse light curve (ascii).',
			  type='string')
	parser.add_option('-w','--window',
			  help = 'File with window information. Regions to fit (x0 x1).',
			  type='string')
	parser.add_option('-o','--output',
			  help = 'File to store result',
			  type='string')

	opt,args = parser.parse_args(argv)

	cl = np.loadtxt(opt.file,unpack=True)
	
	window = np.loadtxt(opt.window,unpack=True)

	mask = np.zeros(len(cl[0]))==0
	for i in range(len(window[0])):
		mm = np.bitwise_not(np.bitwise_and(cl[0] > window[0][i],cl[0] < window[1][i]))
		mask = np.bitwise_and(mask,mm)
	mask = np.bitwise_not(mask)
	
	p = np.polyfit(cl[0][mask],cl[1][mask],3)
	fit = np.polyval(p,cl[0])

	py.plot(cl[0],cl[1],'.')
	py.plot(cl[0][mask],cl[1][mask],'o')
	py.plot(cl[0],np.polyval(p,cl[0]),'-')
	py.plot(cl[0],cl[1]/fit*np.mean(fit),'ro')
	py.show()
	
	if opt.output:
		np.savetxt(	opt.output,
					X = zip(cl[0],cl[1]/fit*np.mean(fit),cl[2]),
					fmt='%+.6f %f %e')

	return 0
######################################################################

if __name__ == '__main__':

	main(sys.argv)