#! /usr/bin/rnv python

'''
	Test resample of spectra.
	
	C - Tiago Ribeiro
'''

import sys,os
import numpy as np
import matplotlib.pyplot as py
from astropy.io import fits as pyfits
import specfitF as spf
import logging

################################################################################

def main(argv):

	logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
						level=logging.DEBUG)

	############################################################################
	# input def
	
	_path = '/Volumes/TiagoSD/Documents/specfit/'

	_spt = 'test_GridNextGen-1.5a+0.4.lis'

	_spobs = 'spec-2826-54389-0590.fits'

	#
	############################################################################
	# setup

	spMod = spf.SpecFit(1)

	spMod.loadSDSSFits(os.path.join(_path,_spobs),True)

	spMod.grid_ndim[0] = 2
	
	spMod.loadPickleTemplate(0,os.path.join(_path,_spt))

	spMod.normTemplate(0,5500.,5520.)

	#
	############################################################################
	#
	
	spMod.scale[0] = 0.4
	spMod.ntemp[0] = 0
	spMod.ntemp[0] = 6
	
	modspec = spMod.modelSpec()
	gridspec = spMod.template[0][6]
	py.plot(gridspec.x,gridspec.flux*spMod.scale[0]*spMod.templateScale[0][6])
	py.plot(spMod.ospec.x,spMod.ospec.flux)
	py.plot(modspec.x,modspec.flux)
	py.show()

	#
	############################################################################
	#

################################################################################

if __name__ == '__main__':

	main(sys.argv)

################################################################################