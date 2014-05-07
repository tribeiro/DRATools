#! /usr/bin/env python

'''
	Simple spectroscopic fit. For testing purposes.
'''

import sys,os
import pylab as py
import logging
from specfit.specfitF import *
from scipy.optimize import leastsq

######################################################################

def main(argv):


	logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',level=logging.INFO)
	
	_path = os.path.expanduser('~/Documents/template')

	#dfile = 'spec-0283-51959-0133.fits'
	dfile = 'fake-0283-51959-0133.npy'
	tlist = 'template_npy.lis'
	
	spf = SpecFit(1)
	#spf.loadSDSSFits(os.path.join(_path,dfile),True)
	spf.loadPickle(os.path.join(_path,dfile))
	spf.loadPickleTemplate(0,os.path.join(_path,tlist))
	#spf.loadtxtTemplate(0,os.path.join(_path,tlist))
	spf.preprocTemplate()

	#spf.saveTemplates2Pickle(0,os.path.join(_path,tlist))
	
	#return 0
	chi2 = np.zeros(len(spf.template[0]))
	scale = np.zeros(len(spf.template[0]))
	vel = np.zeros(len(spf.template[0]))
		
	for ntemp in range(len(spf.template[0])):
	
		logging.info('Template %i'%ntemp)
		
		spf.ntemp[0] = ntemp
		
		p0  = [1e-3,1e-3]
		
		sol,cov,info,mesg,ier = leastsq(spf.chi2,
										p0,
										full_output=True)

		chi2[ntemp] = np.sum(spf.chi2(sol)**2.)
		scale[ntemp] = sol[0]
		vel[ntemp] = sol[1]
		spf.scale[0] = sol[0]
		spf.vel[0] = sol[1]
		model = spf.modelSpec()
		#py.plot(model.x,model.flux,'-',color='r',alpha=0.25)
		logging.info('Solution, score = %e scale = %e, rv = %f km/s'%(chi2[ntemp],scale[ntemp],vel[ntemp]))

	py.subplot(212)

	spf.ntemp[0] = chi2.argmin()
	spf.scale[0] = scale[chi2.argmin()]
	model1 = spf.modelSpec()
	model2 = spf.template[0][chi2.argmin()]
	py.plot(spf.ospec.x,spf.ospec.flux,'k-')
	py.plot(model2.x,model2.flux*spf.scale[0],'b-')
	py.plot(model1.x,model1.flux,'r-')
		
	logging.info('Best-fit template is %s[%i], score = %e scale = %e, rv = %f'%(spf.templateNames[0][chi2.argmin()],chi2.argmin(),chi2.min(),scale[chi2.argmin()],vel[chi2.argmin()]))

	
	#print chi2
	py.subplot(211)
	py.plot(chi2,'o-')
	#py.subplot(212)
	#py.plot(scale,'o-')

	#py.show()
	#return 0
	
	#print sol
	#spf.normTemplate(0,5900.,6100)

	#spf.ntemp[0] = 8
	'''
	p0  = [1e-3]
	
	sol,cov,info,mesg,ier = leastsq(spf.chi2,
									p0,
									full_output=True)
	'''

	#print spf.chi2(sol)
	

	#py.subplot(212)
	#py.plot(spf.ospec.x,(spf.ospec.flux-model.flux) / np.sqrt(model.flux))
	
	py.show()


######################################################################

if __name__ == '__main__':

	main(sys.argv)