#! /usr/bin/env python

'''
	Prepare UX UMA light curves for analysis.
	
	c - Tiago Ribeiro 05/07/2014
'''

import os,sys
import numpy as np
import pylab as py
from astropy.io import fits as pyfits
from astropy.coordinates import ICRS
from astropy import units as u

sys.path.append(os.path.expanduser('~/Develop/astrolibpy/astrolib'))

from helio_jd import helio_jd

######################################################################

def boxcar(x,y,err,size):
	'''
		'''
	
	new_x = np.arange(x.min()+size/2.,x.max()+size,size)
	new_y = np.zeros_like(new_x)
	new_e = np.zeros_like(new_x)
	
	for bin in range(len(new_x)):
		
		mask = np.bitwise_and( x > new_x[bin]-size/2., x < new_x[bin]+size/2.)
		
		new_y[bin] = np.mean(y[mask])
		new_e[bin] = (np.std(y[mask])+np.mean(err[mask]))/2.
	
	return new_x,new_y,new_e

######################################################################

def clproc(table,pshift=0.,plot=False):
	
	T0 = 2452437.56284251 #2452748.38852796
	#Julian Date: 2452748.388527963
	#Heliocentric Julian Date: 2452748.388633476
	HJD0 = 2443904.87872
	Porb =  0.196671278
	phaselim = [-0.2, 0.2]
	
	ra = '07:55:05.3'
	dec = '+22:00:06'
	coords = ICRS(ra,dec,unit=(u.hourangle,u.degree))
	
	time = T0 + (table[1].data['TIME'] - table[1].data['TIME'][0])/60./60./24.
	time_hjd = helio_jd(time - 2400000., coords.ra.deg, coords.dec.deg)+2400000.
	#time_hjd = table[1].data['TIME']/86400.+2450814.5000
	#time_hjd = time
	
	print '%.8f'%time[0]
	print '%.8f'%time_hjd[0]
	
	phase = (time - HJD0) / Porb
	rate_all = table[1].data['RATE']
	error_all = table[1].data['ERROR']
	
	ciclo = np.floor(phase)
	
	nciclo = np.unique(ciclo)
	tt = phase-ciclo
	tt-=pshift
	
	tt[tt > 0.5] -= 1.0
	print '# - There are %i cycles observed...'%len(nciclo)
	print '# - Cycles: [',
	for i in nciclo:
		print '%i '%i,
	print ']'

	'''
		for i in range(len(nciclo)):
		
		
		mask = ciclo == nciclo[i]
		py.errorbar(	tt[mask],
		rate_all[mask],
		error_all[mask],
		fmt='rs',
		capsize=0)
		'''
	
	sort = tt.argsort()
	
	tt = tt[sort]
	rate_all = rate_all[sort]
	error_all = error_all[sort]
	
	mask = np.bitwise_and(tt > phaselim[0], tt < phaselim[1])
	print tt
	if plot:
		py.subplot(211)
		py.errorbar(phase-nciclo[1],table[1].data['RATE'],table[1].data['ERROR'],fmt='.')
		py.subplot(212)
		py.plot(tt,
				rate_all,
				'.')
				
		'''
			py.errorbar(	tt[mask],
			rate_all[mask],
			error_all[mask],
			fmt='rs:',
			capsize=0)
			'''
		#py.plot(nx,ny,linestyle='steps-mid')
		#py.errorbar(nx,ny,ne,fmt = '_',capsize=0)

		#py.ylim(0.,2)
		#py.xlim(-0.2,0.2)
		py.grid()
		py.xlabel('Phase')
		py.ylabel('Counts')
	#py.show()
	
	return tt[mask],rate_all[mask],error_all[mask]

######################################################################

def main(argv):
	
	_path = os.path.expanduser('/Volumes/TiagoHD2/analise/UXUma/')
	_file5 = 'uxuma_0084190201_b50s_0310keV_pn_lc_net.ds'
	
	_ofile5 = 'uxuma.dat.%i'
	
	tb5 = pyfits.open(os.path.join(_path,_file5))
	
	pshift = 0 #0.02298144 #0.02136204
	
	phase,flux,err = clproc(tb5,0,True)
	
	'''
		np.savetxt(	os.path.join(_path,_ofile5%(len(phase))),
		X = zip(phase-pshift,flux,err),
		fmt = '%+.6f %f %e')
		'''
	py.show()
	
	return 0

######################################################################

if __name__ == '__main__':
	
	main(sys.argv)

######################################################################