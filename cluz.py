#! /usr/bin/env python

'''
	Show CAL 87 light curves for analysis purposes. 
	
	c - Tiago Ribeiro 16/12/2013
'''

import os,sys
import numpy as np
import pylab as py
import pyfits
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

	T0 =         2452748.38852796
	#Julian Date: 2452748.388527963
	#Heliocentric Julian Date: 2452748.388633476
	HJD0 = 2450111.5144
	Porb =  0.44267714
	phaselim = [-0.2, 0.2]
	
	ra = '05:46:46.392'
	dec = '-71:08:53.88'
	coords = ICRS(ra,dec,unit=(u.hourangle,u.degree))

	time = T0 + (table[1].data['TIME'] - table[1].data['TIME'][0])/60./60./24.
	#time_hjd = helio_jd(time - 2400000., coords.ra.degrees, coords.dec.degrees)+2400000.
	time_hjd = table[1].data['TIME']/86400.+2450814.5000
	#time_hjd = time
	
	print '%.8f'%time[0]
	print '%.8f'%time_hjd[0]
	
	phase = (time_hjd - HJD0) / Porb
	rate_all = table[1].data['RATE_ALL']
	error_all = table[1].data['ERROR_ALL']

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
	
	if plot:
		py.plot(tt,
				rate_all/np.mean(rate_all),
				'-')

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

	_path = os.path.expanduser('~/Documents/analise/CAL87/')
	#_file1 = 'cal87_0153250101_b250s_0305keV_master_pnm1m2.tfits'
	#_file2 = 'cal87_0153250101_b250s_031keV_master_pnm1m2.tfits'
	#_file3 = 'cal87_0153250101_b250s_051keV_master_pnm1m2.tfits'
	#_file4 = 'cal87_0153250101_b250s_0514keV_master_pnm1m2.tfits'
	#_file1 = 'cal87_0153250101_b250s_0814keV_master_pnm1m2.fits'
	#_file2 = 'cal87_0153250101_b250s_114keV_master_pnm1m2.fits'
	_file5 = 'cal87_0153250101_b250s_0714keV_master_pnm1m2.fits'
	
	#_ofile1 = 'cal87_0305keV_rateall.dat.%i'
	#_ofile2 = 'cal87_031keV_rateall.dat.%i'
	#_ofile3 = 'cal87_051keV_rateall.dat.%i'
	#_ofile4 = 'cal87_0514keV_rateall.dat.%i'
	#_ofile1 = 'cal87_0814keV_rateall.dat.%i'
	#_ofile2 = 'cal87_114keV_rateall.dat.%i'
	_ofile5 = 'cal87_0714keV_rateall.dat.%i'
			
	#tb1 = pyfits.open(os.path.join(_path,_file1))
	#tb2 = pyfits.open(os.path.join(_path,_file2))
	#tb3 = pyfits.open(os.path.join(_path,_file3))
	#tb4 = pyfits.open(os.path.join(_path,_file4))
	tb5 = pyfits.open(os.path.join(_path,_file5))
		
	#py.subplot(311)
	
	pshift = 0 #0.02298144 #0.02136204
	
	#phase,flux,err = clproc(tb1,0.02298144,True)
	#phase,flux,err = clproc(tb1,0.0,True)
	#np.savetxt(	os.path.join(_path,_ofile1%(len(phase))),
	#			X = zip(phase-pshift,flux,err),
	#			fmt = '%+.6f %f %e')

	#py.subplot(312)
	
	#phase,flux,err = clproc(tb2,0,True)

	#np.savetxt(	os.path.join(_path,_ofile2%(len(phase))),
	#			X = zip(phase-pshift,flux,err),
	#			fmt = '%+.6f %f %e')

	#py.subplot(313)
	
	#phase,flux,err = clproc(tb2,0.02298144,True)

	#np.savetxt(	os.path.join(_path,_ofile2%(len(phase))),
	#			X = zip(phase-pshift,flux,err),
	#			fmt = '%+.6f %f %e')

	#phase,flux,err = clproc(tb5,0.015,True)
	phase,flux,err = clproc(tb5,0.02298144,True)
	
	np.savetxt(	os.path.join(_path,_ofile5%(len(phase))),
				X = zip(phase-pshift,flux,err),
				fmt = '%+.6f %f %e')

	py.show()
	
	return 0

######################################################################

if __name__ == '__main__':

	main(sys.argv)

######################################################################