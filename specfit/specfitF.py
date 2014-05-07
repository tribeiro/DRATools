
'''
	specfitF.py - Definition of class for fitting linear combination of spectra.
'''

######################################################################

import numpy as np
import pyfits
from astropysics import spec
import scipy.ndimage.filters
import scipy.constants
import logging

_c_kms = scipy.constants.c / 1.e3  # Speed of light in km s^-1
DF = -8.0

class SpecFit():
	
	##################################################################
	
	def __init__(self,nspec):

		'''
Initialize class. 
	Input:
		nspec = Number of spectra that composes the observed spectra
		'''

		# number of componentes
		self.nspec = nspec

		# Store template spectra
		self.template = [ [] ]*nspec
		self.templateNames = [ [] ]*nspec
				
		# velocity for each component
		self.vel = np.zeros(nspec)
		
		# scale factor for each component
		self.scale = np.zeros(nspec)+1.
		#self.mcscale = pm.Uniform("scale", 0, 1, size=nspec)
		
		# template selected for each component
		self.ntemp = np.zeros(nspec,dtype=int)

		# template grid dimensions for each component
		self.grid_ndim = np.zeros(nspec,dtype=int)
		
		# Grids
		self.Grid = [ [] ]*nspec
		
		# store the observed spectra
		self.ospec = None
		
				
	##################################################################

	def loadtxtTemplate(self,ncomp,filename):
		'''
Loads template spectra from a list of files (in filename), for 
component ncomp.
		'''
		
		splist = np.loadtxt(filename,unpack=True,usecols=(0,),
							dtype='S',ndmin=1)
		
		self.template[ncomp] = [0]*len(splist)


		logging.debug('Loading template spectra for component %i from %s[%i]'%(ncomp,filename,len(splist)))

		for i in range(len(splist)):
			
			logging.debug('Reading %s'%(splist[i]))
			sp = np.loadtxt(splist[i],unpack=True,usecols=(0,1),
							converters={0:lambda s: float(s.replace('D','e')),
										1:lambda s: float(s.replace('D','e'))})
			self.template[ncomp][i] = spec.Spectrum(sp[0],10**sp[1])

		return 0

	##################################################################

	def loadPickleTemplate(self,ncomp,filename):
		'''
Loads template spectra from a list of files (in filename), for 
component ncomp.
		'''
		
		splist = np.loadtxt(filename,unpack=True,
							dtype='S',ndmin=2)
		if splist.shape[0] < self.grid_ndim[ncomp]:
			raise IOError('Grid dimensions is not consistent with expected. Expecting %i got %i.'%(self.grid_ndim[ncomp],splist.shape[0]))
		
		self.template[ncomp] = [0]*len(splist[0])
		self.templateNames[ncomp] = [0]*len(splist[0])
		
		if self.grid_ndim[ncomp] > 0:
			grid = splist[1:self.grid_ndim[ncomp]+1]
			index = np.arange(len(splist[0])).reshape((len(np.unique(grid[0])),len(np.unique(grid[1]))))
			self.Grid[ncomp] = index

		logging.debug('Loading template spectra for component %i from %s[%i]'%(ncomp,filename,len(splist)))

		for i in range(len(splist[0])):
			
			logging.debug('Reading %s'%(splist[0][i]))
			sp = np.load(splist[0][i])
			self.template[ncomp][i] = spec.Spectrum(sp[0],sp[1])
			self.templateNames[ncomp][i] = splist[0][i]

		return 0


	##################################################################

	def loadPickle(self,filename,linearize=True):
		'''
Loads observed spectra from numpy pickle file.
		'''
		
		logging.debug('Loading observed spectra for from %s'%(filename))

		sp = np.load(filename)

		self.ospec = spec.Spectrum(sp[0],sp[1])

		if linearize and not self.ospec.isLinear():
			logging.info('Linearizing observed spectra')
			self.ospec.linearize()

		return 0


	##################################################################

	def loadtxtSpec(self,filename):
		'''
Load the observed spectra.
		'''

		logging.debug('Loading observed spectra for from %s'%(filename))
		
		sp = np.loadtxt(filename,unpack=True,usecols=(0,1),
						converters={0:lambda s: float(s.replace('D','e')),
									1:lambda s: float(s.replace('D','e'))})

		self.ospec = spec.Spectrum(sp[0],sp[1])

		return 0

	##################################################################

	def loadSDSSFits(self,filename,linearize=False):
		'''
Load the observed spectra.
		'''
		
		logging.debug('Loading observed spectra for from %s'%(filename))
		
		sp = pyfits.open(filename)

		self.ospec = spec.Spectrum(	10**(sp[1].data['loglam']),
									sp[1].data['flux'])

		if linearize and not self.ospec.isLinear():
			logging.info('Linearizing observed spectra')
			self.ospec.linearize()
			
		return 0

	##################################################################

	def chi2(self,p):
		'''
Calculate chi-square of the data against model.
		'''

		for i in range(self.nspec):
			logging.debug('%f / %f'%(p[i],p[i+1]))
			self.scale[i] = p[i*2]
			self.vel[i] = p[i*2+1]
			
		model = self.modelSpec()

		#c2 = np.mean( (self.ospec.flux - model.flux )**2.0 / self.ospec.flux)
		c2 = self.ospec.flux - model.flux
		return c2

	##################################################################

	def modelSpec(self):
		'''
Calculate model spectra.
		'''
		
		#_model = self.template[0][self.ntemp[0]]

		logging.debug('Building model spectra')
		
		_model = spec.Spectrum(	self.template[0][self.ntemp[0]].x,
								self.template[0][self.ntemp[0]].flux)

		_model.flux*=self.scale[0]
		_model.x *= np.sqrt((1.0 + self.vel[0]/_c_kms)/(1. - self.vel[0]/_c_kms))

		for i in range(1,self.nspec):

			tmp = spec.Spectrum(self.template[i][self.ntemp[i]].x,
								self.template[i][self.ntemp[i]].flux)
								
			tmp.x *= np.sqrt((1.0 + self.vel[i]/_c_kms)/(1. - self.vel[i]/_c_kms))
			tmp = spec.Spectrum(*tmp.resample(_model.x,replace=False))
			
			_model.flux += self.scale[1]*tmp.flux
		
		if not _model.isLinear():
			logging.warning('Data must be linearized...')
			
		logging.debug('Applying instrument signature')
		
		kernel = self.obsRes()/np.mean(_model.x[1:]-_model.x[:-1])
		
		_model.flux = scipy.ndimage.filters.gaussian_filter(_model.flux,kernel)
		
		logging.debug('Resampling model spectra')
		_model = spec.Spectrum(*_model.resample(self.ospec.x,replace=False))
		return _model

	##################################################################

	def normTemplate(self,ncomp,w0,w1):
		'''
Normalize spectra against data in the wavelenght regions
		'''

		for i in range(len(self.template[ncomp])):
			maskt = np.bitwise_and(	self.template[ncomp][i].x > w0,
									self.template[ncomp][i].x < w1)
			mask0 = np.bitwise_and(	self.ospec.x > w0,
									self.ospec.x < w1)
			
			scale = np.mean(self.ospec.flux[mask0])/np.mean(self.template[ncomp][i].flux[maskt])

			self.template[ncomp][i].flux *= scale
	##################################################################

	def gaussian_filter(self,ncomp,kernel):

		for i in range(len(self.template[ncomp])):
			if not self.template[ncomp][i].isLinear():
				logging.warning('Spectra must be linearized for gaussian filter...')
				
			self.template[ncomp][i].flux = scipy.ndimage.filters.gaussian_filter(self.template[ncomp][i].flux,kernel)

	##################################################################

	def obsRes(self):
		return np.mean(self.ospec.x[1:]-self.ospec.x[:-1])

	##################################################################

	def preprocTemplate(self):
		'''
Pre-process all template spectra to have aproximate coordinates as
those of the observed spectrum and linearize the spectrum.
		'''
	
		logging.debug('Preprocessing all template spectra. Spectra will be trimmed and linearized')
				
		ores = self.obsRes()
		xmin = self.ospec.x[0] -4.0*ores
		xmax = self.ospec.x[-1]+4.0*ores
		
		for i in range(self.nspec):
			for j in range(len(self.template[i])):
				#t_res = np.mean(self.template[i][j].x[1:]-self.template[i][j].x[:-1])
				#newx = np.arange(xmin,xmax,t_res)
				#self.template[i][j] = spec.Spectrum(*self.template[i][j].resample(newx,replace=False))

				self.template[i][j].linearize(lower=xmin, upper=xmax)

	##################################################################

	def saveTemplates2Pickle(self,ncomp,filename):

		splist = np.loadtxt(filename,unpack=True,usecols=(0,),
							dtype='S',ndmin=1)

		logging.debug('Saving template spectr to pickle file...')
		
		for ntemp in range(len(self.template[ncomp])):
			logging.debug(splist[ntemp])
			sp = np.array(	[self.template[ncomp][ntemp].x,
							self.template[ncomp][ntemp].flux])
			np.save(splist[ntemp],sp)
			
	##################################################################

	def suitableScale(self):
		'''
Find a suitable scale values for all spectra.
		'''

		logging.debug('Looking for suitable scale in all spectra. Will choose the larger value.')
		
		obsmean = np.mean(self.ospec.flux)
		maxscale = 0.
		minscale = obsmean

		for i in range(len(self.template)):
			for j in range(len(self.template[i])):
				maskt = np.bitwise_and(	self.template[i][j].x > self.ospec.x[0],
										self.template[i][j].x < self.ospec.x[-1])

				nscale = obsmean/np.mean(self.template[i][j].flux[maskt])

				if maxscale < nscale:
					maxscale = nscale
				if minscale > nscale:
					minscale = nscale

		return maxscale,minscale

######################################################################