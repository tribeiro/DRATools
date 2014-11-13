
'''
	PROGRID - Process Grid.
'''

import os
import numpy as np
from scipy import interpolate as itrp
from astropy.table import Table
import logging as log

################################################################################

class ProGrid():

	############################################################################
	
	def __init__(self):
	
		self._hasTeff_ = False
		self._hasLogg_ = False
		self._hasMet_ = False
	
	############################################################################

	def Teff(self,indx):

		if self._hasTeff_:
			return itrp.splev(indx,self._teffc)
		else:
			log.warning('Teff not defined')
			return 0

	############################################################################

	def logg(self,indx):

		if self._hasLogg_:
			return itrp.splev(indx,self._loggc)
		else:
			log.warning('Logg not defined')
			return 0

	############################################################################

	def metal(self,indx):

		if self._hasMet_:
			return itrp.splev(indx,self._metc)
		else:
			log.warning('Metalicity not defined')
			return 0

	############################################################################

################################################################################

class WDgrid(ProGrid):

	############################################################################

	def __init__(self,tname):
		
		#super(ProGrid, self).__init__()
		
		# Process Grid - Translates the names of the files to parameter values
		self.pgrid(tname)

	############################################################################

	def pgrid(self,tname):

		self._hasTeff_ = True
		self._hasLogg_ = True
		self._hasMet_ = False
		
		grid = Table.read(tname,format='ascii.no_header')

		len_teff = len(np.unique(grid['col2']))
		len_logg = len(np.unique(grid['col3']))

		# Reads Teff

		self.gteff = np.zeros(len_teff)

		for i,ii in enumerate(np.arange(len_teff)*len_logg):
			self.gteff[i] = np.float(os.path.basename(grid['col1'][ii])[2:].split('_')[0])

		# Reads logg
		
		self.glogg = np.zeros(len_logg)

		for i,ii in enumerate(np.arange(len_logg)):
			self.glogg[i] = np.float(os.path.basename(grid['col1'][ii]).split('_')[1].split('.')[0])

		# evalute grid interpolation

		self._teffc = itrp.splrep(np.arange(len_teff),self.gteff)
		self._loggc = itrp.splrep(np.arange(len_logg),self.glogg)

	############################################################################

################################################################################


class MDgrid(ProGrid):

	############################################################################

	def __init__(self,tname):
		
		#super(ProGrid, self).__init__()
		
		# Process Grid - Translates the names of the files to parameter values
		self.pgrid(tname)

	############################################################################

	def pgrid(self,tname):

		self._hasTeff_ = True
		self._hasLogg_ = True
		self._hasMet_ = True
		
		grid = Table.read(tname,format='ascii.no_header')

		len_met = len(np.unique(grid['col2']))
		len_teff = len(np.unique(grid['col3']))
		len_logg = len(np.unique(grid['col4']))
		
		# Reads Teff

		self.gteff = np.zeros(len_teff)

		for i,ii in enumerate(np.arange(len_teff)*len_logg):
			self.gteff[i] = np.float(os.path.basename(grid['col1'][ii])[5:].split('-')[0])*100.

		# Reads logg
		
		self.glogg = np.zeros(len_logg)

		for i,ii in enumerate(np.arange(len_logg)):
			self.glogg[i] = np.float(os.path.basename(grid['col1'][ii]).split('-')[1])*-1.0

		# Reads Metalicity
		
		self.gmet = np.zeros(len_met)

		for i,ii in enumerate(np.arange(len_met)):
			self.gmet[i] = np.float(os.path.basename(grid['col1'][ii]).split('-')[2].split('a')[0])*-1.0

		# evalute grid interpolation

		self._teffc = itrp.splrep(np.arange(len_teff),self.gteff)
		self._loggc = itrp.splrep(np.arange(len_logg),self.glogg)
		if len_met > 3:
			self._metc  = itrp.splrep(np.arange(len_met),self.gmet)
		else:
			self._metc  = itrp.splrep(np.arange(len_met),self.gmet,k=1)

	############################################################################

################################################################################


