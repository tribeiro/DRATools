
'''
	Setup model for pymc fit.
'''

import os
import numpy as np
import pylab as py
import specfitF as spf
import pymc
from pymc import MCMC
import logging

######################################################################

def ModelFactory(ncomp,ofile,templist):
	'''
A factory of model to do the spectroscopic fit with PyMC.

Input:
		ncomp		- The number of spectroscopic components to fit.
		ofile		- The observed spectra.
		templist	- The template list.
	'''

	spMod = spf.SpecFit(ncomp)

	# Load observed spectra as Pickle file
	
	if ofile.rfind('.fits') > 0:
		spMod.loadSDSSFits(ofile,True)
	elif ofile.rfind('.npy') > 0:
		spMod.loadPickle(ofile)
	else:
		raise IOError('Cannot read %s data type. Only fits and numpy (pickle) files are suported.'%(ofile))
	
	# Load template spectra, for each component as Picke files

	spMod.grid_ndim[0] = 2
	for i in range(ncomp):
		spMod.loadPickleTemplate(i,templist[i])

	# Pre-process template files

	spMod.normTemplate(0,5500.,5520.)
	spMod.preprocTemplate()

	# Prepare PyMC stochastic variables

	maxlevel,minlevel = spMod.suitableScale()
	level = maxlevel
	maxlevel *= 2.0
	minlevel /= 2.0

	min,val,max = np.zeros(ncomp)+minlevel,np.zeros(ncomp)+level,np.zeros(ncomp)+maxlevel
	scales = pymc.Uniform('scale', min, max, value=val,size=ncomp)
	min,val,max = np.zeros(ncomp)-300.,np.zeros(ncomp),np.zeros(ncomp)+300.
	velocity = pymc.Uniform('velocity', min, max , value=val,size=ncomp)

	gridmin = np.zeros(ncomp*np.sum(spMod.grid_ndim),dtype=int)
	gridmax = np.zeros(ncomp*np.sum(spMod.grid_ndim),dtype=int)
	for i in range(ncomp):
		gridmax[i*2] = len(spMod.Grid[0])-1
		gridmax[i*2+1] = len(spMod.Grid[0][i])-1

	#max = np.array([len(spMod.template[i])-1 for i in range(ncomp)],dtype=int)
	val = gridmax/2
		
	template = pymc.DiscreteUniform('template', lower=gridmin, upper=gridmax,value=val,
									size=ncomp*np.sum(spMod.grid_ndim))
	# Prepare PyMC deterministic variables
	
	@pymc.deterministic
	def spModel(scales=scales,velocity=velocity,template=template):
		for i in range(len(scales)):
			logging.debug('spModel: %i %e %f %i %i'%(i,scales[i],velocity[i],template[i],template[i+1]))
			spMod.scale[i] = scales[i]
			spMod.vel[i] = velocity[i]
			spMod.ntemp[i] = spMod.Grid[i][template[i]][template[i+1]]
		modspec = spMod.modelSpec()
		return modspec.flux

	mflux = np.mean(spMod.ospec.flux)
	sig = pymc.Uniform('sig', mflux/100., mflux/10., value=mflux/50.)
	y = pymc.Normal('y', mu=spModel, tau=1.0/sig**2, value=spMod.ospec.flux, observed=True)

	return locals()

######################################################################

logging.basicConfig(filename='pymc.log',format='%(levelname)s:%(asctime)s::%(message)s',
					level=logging.DEBUG)

_path = os.path.expanduser('~/Documents/template')

#dfile = 'spec-0283-51959-0133.fits'
#outfile = 'pymc-0283-51959-0133.npy'

dfile = 'spec-1004-52723-0418.fits' # WD Teff = 7459, logg = 7.92
outfile = 'pymc-1004-52723-0418.npy'

#dfile = 'spec-0492-51955-0523.fits' # WD Teff = 6619, logg = 8.27
#outfile = 'pymc-0492-51955-0523.npy'

dfile = 'spec-2420-54086-0499.fits'
outfile = 'pymc-2420-54086-0499.npy'

#dfile = 'da07500_725.npy' # WD Teff = 6619, logg = 8.27
#outfile = 'pymc-07500_725.npy'

#dfile = 'fake-0283-51959-0133.npy'
#outfile = 'fpymc-0283-51959-0133.npy'

#tlist = 'template_npy.lis'
#tlist = 'template1_wd.lis'
#tlist = 'template2_wd.lis'
tlist = 'template3_wd.lis'

M = pymc.MCMC(	ModelFactory( 1, os.path.join(_path,dfile),[os.path.join(_path,tlist)] ) ,
				db = 'pickle')


'''
py.plot(M.spMod.ospec.x,M.spMod.ospec.flux,'r')
for i in range(len(M.spMod.template[0])):
	M.spMod.ntemp[0] = i
#print M.spMod.Grid

	mspec = M.spMod.modelSpec()
	py.plot(mspec.x,mspec.flux,'b')


py.show()

'''

M.sample(iter=10000, burn=1000,thin=5)#,tune_interval=1000,tune_throughout=True,verbose=0)

grid = np.array(M.trace('template')[:]).reshape(2,-1)

oarray = np.zeros(	len(M.trace('scale')[:]),
					dtype=[('scale', '<f8'), ('velocity', '<f8'), ('temp1', '<i4') , ('temp2', '<i4')])


oarray['scale'] = np.array(	[i[0] for i in M.trace('scale')[:]] )
oarray['velocity'] = np.array(	[i[0] for i in M.trace('velocity')[:]] )
oarray['temp1'] = np.array(	[i[0] for i in M.trace('template')[:]] )
oarray['temp2'] = np.array(	[i[1] for i in M.trace('template')[:]] )

np.save(os.path.join(_path,outfile),oarray)


py.subplot(241)
hh,edges = np.histogram(oarray['scale'],range=[M.minlevel,M.maxlevel*1.2])
width = np.mean(edges[1:]-edges[:-1])/2.
py.bar(edges[:-1],hh+1e-3,width=width)

py.subplot(242)
py.hist(oarray['velocity'])

py.subplot(243)

hh,edges = np.histogram(oarray['temp1'],bins=np.arange(-0.5,24.5))
py.bar(edges[:-1]+0.1,hh+1e-3)

py.subplot(244)
hh,edges = np.histogram(oarray['temp2'],bins=np.arange(-0.5,24.5))
py.bar(edges[:-1]+0.1,hh+1e-3)

py.subplot(212)
mspec = M.spMod.modelSpec()
py.plot(M.spMod.ospec.x,M.spMod.ospec.flux)
py.plot(mspec.x,mspec.flux)

logging.info('Done')

py.show()

