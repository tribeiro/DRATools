#! /usr/bin/env python

'''
	Show CAL 87 light curves for analysis purposes. 
	
	c - Tiago Ribeiro 16/12/2014
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
	phase-=pshift
	
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
	
	#tt = tt[sort]
	#rate_all = rate_all[sort]
	#error_all = error_all[sort]
	
	#mask = np.bitwise_and(tt > phaselim[0], tt < phaselim[1])
	
	return tt,phase,rate_all,error_all

######################################################################

def main(argv):

	_path = os.path.expanduser('~/Documents/analise/CAL87/')
	_file1 = 'cal87_0153250101_b250s_0305keV_master_pnm1m2.tfits'
	_file2 = 'cal87_0153250101_b250s_031keV_master_pnm1m2.tfits'
	_file3 = 'cal87_0153250101_b250s_051keV_master_pnm1m2.tfits'
	_file4 = 'cal87_0153250101_b250s_0514keV_master_pnm1m2.tfits'
	
	_ofile1 = 'cal87_0305keV_rateall.dat.%i'
	_ofile2 = 'cal87_031keV_rateall.dat.%i'
	_ofile3 = 'cal87_051keV_rateall.dat.%i'
	_ofile4 = 'cal87_0514keV_rateall.dat.%i'
			
	_opath = os.path.expanduser('~/Dropbox/Documents/paper_cal87/Figures')
	_oname = 'cal87_lightcurves.pdf'

	tb1 = pyfits.open(os.path.join(_path,_file1))
	tb2 = pyfits.open(os.path.join(_path,_file2))
	tb3 = pyfits.open(os.path.join(_path,_file3))
	tb4 = pyfits.open(os.path.join(_path,_file4))
		
	#py.subplot(311)
	
	pshift = 0 #0.02298144 #0.02136204
		
	phase,cycle,flux,err = clproc(tb1,0.,True)
	
	nciclos = np.unique(np.floor(cycle))[1:]
		
	ax1 = py.subplot(211)
		
	py.errorbar(cycle-nciclos[0],flux,err,fmt='r.',capsize=0)

	ylim = [0.001,2] #py.ylim()
	
	for n in [0,1]:
		print '-->',n
		py.plot([n+0.02298144,n+0.02298144],ylim,'k--')
		py.plot([n,n],ylim,'k:')
	py.ylim(ylim)
	
	phase,cycle,flux,err = clproc(tb4,0.,True)

	ax2 = py.subplot(212)

	nciclos = np.unique(np.floor(cycle))[1:]
		
	py.errorbar(cycle-nciclos[0],flux,err,fmt='r.',capsize=0)

	ylim = [0,2] #py.ylim()
	
	for n in [0,1]:
		print '-->',n
		py.plot([n+0.02298144,n+0.02298144],ylim,'k--')
		py.plot([n,n],ylim,'k:')
	py.ylim(ylim)

	py.setp(ax1.get_xticklabels(),visible=False)
	py.subplots_adjust(hspace=0.)

	figtitle = {0:'Soft (0.3 - 0.5 keV)',1:'031',2:'Hard (0.5 - 1.4 keV)'}
	ax1.annotate(figtitle[0], rotation=-90, xy=(1.05, .5),  xycoords='axes fraction',
                horizontalalignment='center', verticalalignment='center',size=18)
	ax2.annotate(figtitle[2], rotation=-90, xy=(1.05, .5),  xycoords='axes fraction',
                horizontalalignment='center', verticalalignment='center',size=18)

	ax2.set_xlabel('Cycle - 11840',size=20)
	ax1.set_ylabel('Count rate',size=20)
	ax2.set_ylabel('Count rate',size=20)

	print '# - Saving figure @: %s'%(os.path.join(_opath,_oname))
	py.savefig(os.path.join(_opath,_oname))

	py.show()
	
	return 0

######################################################################

if __name__ == '__main__':

	main(sys.argv)

######################################################################