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
	xx = np.arange(0,360,30./24./60./60.)

	# Fixed orbital period
	P1 = 2.0
	# build observations
	yy1 = np.sin(xx*2.*np.pi/P1) # data
	err = np.random.exponential(0.1,len(xx))*(-1)**np.random.randint(0,2,len(xx))
	# Running dft
	t = np.arange(0.45,0.55,0.001) # defining frequency range
	dd = dft(xx,yy1+err,t) # run
	period = 1./t[dd.argmax()] # Peak is periodicity (should fit a gaussian?)
	phase = xx/period
	phase = phase - np.floor(phase)
	py.subplot(211)
	py.plot(phase,yy1+err,'.')
	
	py.subplot(212)
	py.plot(1./t,dd,ls='steps-mid')
	ylim = py.ylim()
	py.plot([period,period],ylim,'r--')
	
	py.show()
	return 0
	
	npieces = 4 #int(np.floor(xx[-1]/period/2.))
	p = 10.
	
	dP2 = 365.*p # Period of period variations in years
	P2 = P1+1e-2*np.sin(xx*2.*np.pi/dP2)
	yy2 = np.sin(xx*2.*np.pi/P2)

	pp = piecewise_dft(npieces,xx,yy2,t)

	ppp = np.zeros(len(pp[0]))
	for i in range(len(pp)):
		ppp += pp[i]
	ppp /= len(pp)

	#py.plot(1./t,ppp,ls='steps-mid')
	sz = len(xx)/npieces
	
	for i in range(len(pp)):
		#py.plot(1./t,pp[i],ls='steps-mid')
		period = 1./t[pp[i].argmax()]
		
		print period,np.mean(P2[sz*i:sz*(i+1)]),P2[(sz*i+sz*(i+1))/2.]
		py.plot([period,period],ylim,'--')
		py.plot([np.mean(P2[sz*i:sz*(i+1)]),np.mean(P2[sz*i:sz*(i+1)])],ylim,':')

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