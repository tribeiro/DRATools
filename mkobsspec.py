#! /usr/bin/env python

'''
	Take model spectrum, aply scaling factor, instrumental signature and wavelenght degrading
	and save as observed spectra.
'''

import sys,os
import pylab as py
import logging
from specfit.specfitF import *

def main(argv):

	logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',level=logging.INFO)
	
	_path = os.path.expanduser('~/Documents/template')

	dfile = 'spec-0283-51959-0133.fits'
	tlist = 'template2_wd.lis' # lte078-0.0-0.0a+0.0.BT-NextGen.7.npy
	ofile = 'fake-0283-51959-0133'
	
	spf = SpecFit(1)
	spf.loadSDSSFits(os.path.join(_path,dfile),True)
	spf.loadPickleTemplate(0,os.path.join(_path,tlist))
	
	spf.preprocTemplate()

	spf.ntemp[0] = 135
	savespec = spf.modelSpec()

	err = np.random.exponential(np.mean(savespec.flux)/20.,len(savespec.flux))
	err *= (-1)**np.random.randint(0,2,len(savespec.flux))
	
	ofile = os.path.basename(spf.templateNames[0][spf.ntemp[0]])
	logging.info('Writing file %s'%(ofile))
	np.save(os.path.join(_path,ofile),np.array([savespec.x,savespec.flux+err]))
	#py.errorbar(savespec.x,savespec.flux+err,np.mean(savespec.flux)/50.,fmt='.')
	py.plot(savespec.x,savespec.flux+err,'-')
	py.plot(savespec.x,savespec.flux)
	py.plot(spf.template[0][0].x,spf.template[0][0].flux)
	
	py.show()

######################################################################

if __name__ == '__main__':

	main(sys.argv)