#! /usr/bin/env python

'''
	Find minimum on light curve by fitting a gaussian, or a polynome.
	
	c - Tiago Ribeiro 16/12/2014
'''

import os,sys
import numpy as np
import pylab as py
import pyfits
from scipy.optimize import leastsq
from scipy import polyfit,polyval,roots
from optparse import OptionParser
from astropy.stats.funcs import bootstrap

######################################################################

def MC_sim(x,err,nsim):

	mcdata = np.zeros(len(x)*nsim).reshape(nsim,len(x))

	for i in range(nsim):
		simerr = np.random.exponential(scale=err)*-1**(np.random.randint(0,2,len(err)))
		mcdata[i] = x+simerr
	return mcdata

######################################################################

def main(argv):

	##################################################################
	# Parse arguments

	fitopt = {0:'gaussian',1:'2nd order polynome'}
	
	from optparse import OptionParser
	
	parser = OptionParser()
	
	parser.add_option(	'--fittype',
						help='Which type of fit will be performed. Options are %r.'%fitopt,
						type='int',
						default=0)

	opt,args = parser.parse_args(argv)

	print 'Will find minimum by %s fitting...'%(fitopt[opt.fittype])
	##################################################################
	# Parameters
	HJD0 = 2450111.5144
	Porb =  0.44267714
	#
	##################################################################
	# Input definition
	_path = os.path.expanduser('~/Documents/analise/CAL87/emap_0305keV_rateall')
	#_cldat = 'cal87_0305keV_rateall.dat.122' #'cal87_0305keV_rateall.dat.122'
	#_cldat = '../cal87_0153250101_b250s_051keV_master_pnm1m2.tfits' #'cal87_0305keV_rateall.dat.122'
	_cldat = '../cal87_0153250101_b250s_0514keV_master_pnm1m2.tfits' #'cal87_0305keV_rateall.dat.122'
	#_clmod = 'cal87_0305keV_rateall.prd.122'
	#
	##################################################################
	# Reading data
	
	#cldat = np.loadtxt(os.path.join(_path,_cldat),unpack=True)
	#clmod = np.loadtxt(os.path.join(_path,_clmod),unpack=True)
	table = pyfits.open(os.path.join(_path,_cldat))
	time_hjd = table[1].data['TIME']/86400.+2450814.5000
	rate_all = table[1].data['RATE_ALL']
	error_all = table[1].data['ERROR_ALL']
	#
	##################################################################
	# Fitting
	
	if opt.fittype == 0:
	
		phase = (time_hjd - HJD0) / Porb
		phase = phase-np.floor(phase)
		phase[phase > 0.5] -= 1.0
		sort = phase.argsort()
		cldat = np.array([phase[sort],rate_all[sort],error_all[sort]])
		func = lambda p,x: p[0] + p[1]*np.exp(-((x-p[2])/p[3])**2.0)
		fitfunc = lambda p,x,y: y - func(p,x)
		
		p0  = [np.mean(cldat[1]),np.min(cldat[1])-np.mean(cldat[1]),1e-1,0.15]
		
		sol,cov,info,mesg,ier = leastsq(fitfunc,
										p0,
										args=(cldat[0],cldat[1]),
										full_output=True)
	
		print sol
		py.errorbar(	cldat[0],
						cldat[1],
						cldat[2],
						fmt='rs:',
						capsize=0)
		py.plot(cldat[0],
				func(sol,cldat[0]),'k-')
	if opt.fittype == 1:
		# Fit parabola
		phase = (time_hjd - HJD0) / Porb
		ciclos = np.unique(np.floor(phase))
		print '# - %i cycles, fitting %i eclipses...'%(len(ciclos),len(ciclos)-1)

		for i in range(len(ciclos)-1):
			print '## - Fitting from phases [%f:%f]'%(ciclos[i+1]-0.5,ciclos[i+1]+0.5)
			mask = np.bitwise_and(phase >ciclos[i+1]-0.5,phase < ciclos[i+1]+0.5)
			cldat = np.array([phase[mask]-ciclos[i+1],rate_all[mask],error_all[mask]])
			mask = np.bitwise_and(cldat[0] > -0.1, cldat[0]<0.1)
			p,residuals,rank,singular_values,rcond = polyfit(cldat[0][mask],
															 cldat[1][mask],
															 deg=2,full=True)
		
			print '# - Bootstraping...'
			ndata = MC_sim(cldat[1][mask],cldat[2][mask],100)
			bootpar = np.array([p])
			bootroots = np.array([roots(p).real])
			for j in range(len(ndata)):
				bp = polyfit( cldat[0][mask],
							 ndata[j],
							 deg=2,full=False)
				bootpar = np.append(bootpar,bp)
				bootroots = np.append(bootroots,np.roots(bp).real)
			bootpar = bootpar.reshape(-1,3)
			print bootpar.shape,bootpar[0]
			
			print p,singular_values
			print roots(p)
			print bootroots.mean(),'+/-',bootroots.std()
			py.subplot(2,len(ciclos)-1,i+1)
			py.errorbar(	cldat[0][mask],
							cldat[1][mask],
							cldat[2][mask],
							fmt='rs:',
							capsize=0)
			py.plot(cldat[0][mask],
					polyval(p,cldat[0][mask]),'k-')
					
			py.subplot(2,len(ciclos)-1,len(ciclos)-1+i+1)
			py.hist(bootroots,bins=40)

		py.show()
		return 0
		
		
		mask = np.bitwise_and(cldat[0] > -0.05, cldat[0]<0.09)
		p,residuals,rank,singular_values,rcond = polyfit(cldat[0][mask],
														 cldat[1][mask],
														 deg=2,full=True)
		py.errorbar(	cldat[0][mask],
						cldat[1][mask],
						cldat[2][mask],
						fmt='rs:',
						capsize=0)
		py.plot(cldat[0][mask],
				polyval(p,cldat[0][mask]),'k-')
		print p,singular_values
		print roots(p)
		
		
		
	#
	##################################################################
	# End
	
	py.show()
	
	return 0

######################################################################

if __name__ == '__main__':

	main(sys.argv)

######################################################################