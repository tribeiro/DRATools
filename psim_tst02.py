#!/usr/bin/rnv python

'''
Test the effect of changing orbital period on light curves of spoted stars. Consider that the light curve is a sinusoid, with changing period. Tasks are:

	- Generate a light curve for a specific period with specific, long-term period changes
		- Light curve has a specific time resolution and coverage
	- Run lombscargle on entire dataset (see impact of period changes on periodogram)
	- Run lobscargle for running windows (try to identify period changes)
	
	- Future: Take Keppler data.
'''

import sys,os
from optparse import OptionParser
from psimF import *

################################################################################

def main(argv):

	parse = OptionParser()
		
	opt,args = parse.parse_args(argv)

	# build time of observations 30s in 60 days
	xx = np.arange(0,360*5,30./24./60./60.)

	# Fixed orbital period
	P1 = 2.0
	# build observations
	yy1 = np.sin(xx*2.*np.pi/P1) # data
	err = np.random.exponential(0.1,len(xx))*(-1)**np.random.randint(0,2,len(xx))
	# Running dft
	t = np.arange(0.48,0.52,0.0005) # defining frequency range
	dd = dft(xx,yy1+err,t) # run
	period = 1./t[dd.argmax()] # Peak is periodicity (should fit a gaussian?)

	npieces = int(np.floor((xx[-1]-xx[0])/period/30.))
	if npieces < 4:
		npieces = 4
	print 'Running on %i pieces...'%(npieces)

	p = 5.
	
	dP2 = 365.*p # Period of period variations in years
	dPAmp = 1e-3
	P2 = P1+np.zeros_like(xx) #+5e-3*np.sin(xx*2.*np.pi/dP2)

	sz = len(xx)/npieces
	for i in range(npieces):
		P2[sz*i:sz*(i+1)] += dPAmp*np.sin(xx[(sz*i+sz*(i+1))/2.]*2.*np.pi/dP2)

	yy2 = np.sin(xx*2.*np.pi/P2)

	pp = piecewise_dft(npieces,xx,yy2+err,t)
	
	ppp = np.zeros(len(pp[0]))
	for i in range(len(pp)):
		ppp += pp[i]
	ppp /= len(pp)

	#py.plot(1./t,ppp,ls='steps-mid')

	mper1 = np.zeros(npieces)
	mper2 = np.zeros(npieces)
	rper = np.zeros(npieces)

	py.subplot(211)

	for i in range(len(pp)):
		print '-> ',i,
		py.plot(1./t,pp[i],ls='steps-mid')
		pres = findPeriod(1./t,pp[i])
		py.plot(1./t,func(pres,1./t))
		ylim = py.ylim()
		#period = 1./t[pp[i].argmax()]
		
		print pres[1],np.mean(P2[sz*i:sz*(i+1)]),P2[(sz*i+sz*(i+1))/2.],(sz*i+sz*(i+1))/2
		mper1[i] = pres[1]
		mper2[i] = 1./t[pp[i].argmax()]
		rper[i] = P2[(sz*i+sz*(i+1))/2.]
		py.plot([pres[1],pres[1]],ylim,'--')
		py.plot([np.mean(P2[sz*i:sz*(i+1)]),np.mean(P2[sz*i:sz*(i+1)])],ylim,':')

	py.ylim(ylim)

	py.subplot(212)

	tmed = [np.mean(xx[sz*i:sz*(i+1)]) for i in range(len(pp))]

	py.plot(tmed,mper1,'.')
	py.plot(tmed,mper2,'+')
	#py.plot(rper,mper1,'.')
	xymin = np.min(xx)
	xymax = np.max(xx)
	xxx = np.arange(xymin,xymax,0.5)
	py.plot(xxx,P1+dPAmp*np.sin(xxx*2.*np.pi/dP2))
	#py.plot([xymin,xymax],[xymin,xymax],'-')
	#py.plot(rper,mper2,'.')

	py.show()

	return 0

	for p in range(5,5*20,20):
		print p
		dP2 = 365.*p # Period of period variations in years
		P2 = P1+1e-1*np.sin(xx*2.*np.pi/dP2)
		yy2 = np.sin(xx*2.*np.pi/P2)
		
		dd = dft(xx,yy2,t)
			
		py.plot(t,dd,ls='steps-mid')
		
	py.show()
	
	return 0
################################################################################

if __name__ == '__main__':

	main(sys.argv)