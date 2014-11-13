#!/usr/bin/env python

import sys,os
import numpy as np
import pylab as py
from astropy.table import Table

################################################################################

def main(argv):

	############################################################################
	# Path and file definitions

	_path = '/Volumes/TiagoHD2/Documents/specfit/'

	_ifile = 'snr_matchres_csv.hdf5'

	hdf5file = os.path.join(_path,_ifile)
	
	############################################################################
	# Reads input file

	data = Table.read(hdf5file,path = 'data')
	rm12 = Table.read(hdf5file,path = 'RM12')
	xmatch = Table.read(hdf5file,path = 'xmatch')

	mask = data['Teff_1'] < 80000 #np.bitwise_and(data['Teff_1'] < 80000,data['sig'] < 1)
	amask = np.arange(len(data))[mask]
	tmask = rm12['Teffwd']>0
	
	for ii,i in enumerate(amask):

		mm = xmatch['TRidx'] == i
		if not tmask[i]:
			print xmatch[mm]

	############################################################################
	# Plots

	# Compare WD temperature

	#py.subplot(211)
	sig = data['sig'][xmatch['TRidx']]
	data1 = data['Teff_1'][xmatch['TRidx']]

	tmask = np.bitwise_and(tmask,sig < 3)
	py.plot(data1[tmask],rm12['Teffwd'][tmask],'b.')
	py.plot(data1[sig>1.5],rm12['Teffwd'][sig>1.5],'ro')

	py.plot([0,100000],[0,100000],'r-')

	#py.subplot(212)
	#py.plot(data['logg_1'][xmatch['TRidx']],rm12['logg'],'.')
	
	py.show()

	############################################################################

	return 0

	############################################################################

################################################################################

if __name__ == '__main__':

	main(sys.argv)

################################################################################