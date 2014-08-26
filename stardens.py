#! /usr/bin/env python

'''
	Star density map.
	
	C - Tiago Ribeiro
'''

import sys,os
import numpy as np
import matplotlib.pyplot as py
import logging

################################################################################

def distHist(coord,dcoord):

	xgrid = np.arange(np.min(coord['px']),np.max(coord['px']),np.mean(dcoord['dist'])*11)
	ygrid = np.arange(np.min(coord['py']),np.max(coord['py']),np.mean(dcoord['dist'])*11)
	
	hist2d = np.zeros((len(xgrid)-1)*(len(ygrid)-1)).reshape(len(xgrid)-1,len(ygrid)-1)

	for ix in range(len(xgrid)-1):
		for iy in range(len(ygrid)-1):
			mask_x = np.bitwise_and(coord['px']>xgrid[ix],
									coord['px']<xgrid[ix+1])
			mask_y = np.bitwise_and(coord['py']>xgrid[iy],
									coord['py']<xgrid[iy+1])
			mask = np.bitwise_and(mask_x,mask_y)
			hist2d[ix][iy] = np.mean(dcoord['dist'][mask])
	return hist2d

################################################################################

def findCloser(coord):

	dcoord = np.array(np.zeros(len(coord))-1,
					 dtype=[('idx', '<i4'),
							('cidx','<i4'),
							('dist','<f8')])

	index = np.arange(len(coord))
	

	for i in range(len(coord)):
		
		dist = np.sqrt( (coord['px'][i]-coord['px'])**2. + (coord['py'][i]-coord['py'])**2. )
		mask = dist>0
		cidx = dist[mask].argmin()
		dcoord['idx'][i] = i
		dcoord['cidx'][i] = index[mask][cidx]
		dcoord['dist'][i] = dist[mask][cidx]
	
	return dcoord

################################################################################

def main(argv):

	logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
						level=logging.DEBUG)

	from optparse import OptionParser

	parser = OptionParser()

	parser.add_option('--pop_file',
					  help = '''Definition of stellar populations.''',
					  type='int',default=1)
	parser.add_option('-v','--verbose',
					  help = 'Run in verbose mode.',action='store_true',
					  default=False)
	parser.add_option('--savefig',
					  help = 'Save png with output.',action='store_true',
					  default=False)
	parser.add_option('--show',
					  help = 'Show figure with output.',action='store_true',
					  default=False)
	opt,args = parser.parse_args(argv)
	
	NStar1 = 1000
	NStar2 = 10000
	tabxy = np.array(np.zeros(NStar1+NStar2)-1,
					 dtype=[('px', '<f8'),
							('py', '<f8')])

	tabxy['px'][:NStar1] = (np.random.random(NStar1)-0.5)*2
	tabxy['py'][:NStar1] = (np.random.random(NStar1)-0.5)*2

	tabxy['px'][NStar1:NStar1+NStar2] = np.random.exponential(0.1,NStar2)*(-1)**np.random.randint(0,2,NStar2)
	tabxy['py'][NStar1:NStar1+NStar2] = np.random.exponential(0.1,NStar2)*(-1)**np.random.randint(0,2,NStar2)

	dtabxy = findCloser(tabxy)

	dhist = distHist(tabxy,dtabxy)
	'''
	py.figure(1)
	
	py.plot(tabxy['px'],tabxy['py'],'.')
	
	for i in range(len(dtabxy)):
		py.plot([tabxy['px'][dtabxy['idx'][i]],tabxy['px'][dtabxy['cidx'][i]]],
				[tabxy['py'][dtabxy['idx'][i]],tabxy['py'][dtabxy['cidx'][i]]],
				'b-')
	
	py.figure(2)
	'''
	print dtabxy['dist'].mean(),dtabxy['dist'].std()
	py.imshow(np.log10(dhist),interpolation='nearest')
	
	'''
	py.figure(3)
	for i in range(len(dhist)):
		py.plot(np.log10(dhist[i]),'b-')
	'''
	
	py.show()
	
	return 0

################################################################################

if __name__ == '__main__':

	main(sys.argv)