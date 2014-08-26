#! /usr/bin/env python

import sys,os
import logging as log
import pylab as py
import numpy as np
from astropy.io import fits as pyfits

################################################################################

def main(argv):
	'''
Plot variability graph for sources in input file. Input file should be a fits in
SDSS standard with the following columns:

thingId	mjd	TAI_u	TAI_g	TAI_r	TAI_i	TAI_z
psfMag_u	psfMagerr_u	psfMag_g	psfMagerr_g	
psfMag_r	psfMagerr_r	psfMag_i	psfMagerr_i	
psfMag_z	psfMagerr_z

	'''
		
	log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                        level=log.DEBUG)

	from optparse import OptionParser

	parser = OptionParser()

	parser.add_option('-f','--filename',
					help = 'FITS binary table in SDSS format with photometry.'
					,type='string')

	opt,args = parser.parse_args(argv)


	hdu = pyfits.open(opt.filename)

	obj_key = 'thingId'
	time_key = 'TAI_%s'
	mag_key = 'psfMag_%s'
	merr_key = 'psfMagerr_%s'

	band = 'ugriz'
	nband = len(band)

	uobj = np.unique(hdu[1].data[obj_key])

	log.info('Found %i objects'%(len(uobj)))

	for _nob in range(len(uobj)):
		for _nb in range(nband):
			log.debug('%i %i'%(_nob,_nb))

			mask = np.bitwise_and(	hdu[1].data[obj_key] == uobj[_nob],
							  hdu[1].data[mag_key%band[_nb]] > 0 )
			fname = '%s_%s.txt'%(uobj[_nob],band[_nb])
			log.info('Saving %s...'%(fname))
			np.savetxt(fname,
					   fmt="%f %f %f",
					   X=zip(   hdu[1].data[time_key%band[_nb]][mask]/(24*3600),
								hdu[1].data[mag_key%band[_nb]][mask],
								hdu[1].data[merr_key%band[_nb]][mask]))

	return 0
	
	mavg = np.zeros(len(uobj)*nband).reshape(nband,len(uobj))
	mstd = np.zeros(len(uobj)*nband).reshape(nband,len(uobj))
	eavg = np.zeros(len(uobj)*nband).reshape(nband,len(uobj))

	log.debug('%i %i'%mavg.shape)

	for _nob in range(len(uobj)):
		for _nb in range(nband):
			log.debug('%i %i'%(_nob,_nb))
			
			mask = np.bitwise_and(	hdu[1].data[obj_key] == uobj[_nob],
									hdu[1].data[mag_key%band[_nb]] > 0 )
			mavg[_nb][_nob] = np.mean(hdu[1].data[mag_key%band[_nb]][mask])
			mstd[_nb][_nob] = np.std(hdu[1].data[mag_key%band[_nb]][mask])
			eavg[_nb][_nob] = np.mean(hdu[1].data[merr_key%band[_nb]][mask])


	msample = np.arange(14,25,1.0)
	mag = np.zeros(len(msample)*nband).reshape(nband,len(msample))
	std = np.zeros(len(msample)*nband).reshape(nband,len(msample))

	for _nb in range(nband):
		for j in range(len(msample)-1):
			mask = np.bitwise_and(mavg[_nb] > msample[j],
								  mavg[_nb] < msample[j+1])
			#print msample[j],msample[j+1]
			#print mavg[_nb][mask]
			mag[_nb][j] = np.mean(mavg[_nb][mask])
			std[_nb][j] = np.mean(eavg[_nb][mask])

	mainfig = py.figure(1)

	figcount = 2
	figs = []
	axis = []

	for _nb in range(nband):
		mainfigaxis = mainfig.add_subplot(2,2,_nb+1)
		mainfigaxis.plot(msample,std[_nb],'-')
		mainfigaxis.plot(msample,std[_nb]*10,'-')
		mainfigaxis.plot(mavg[_nb],mstd[_nb],'r.')
		mask = mstd[_nb] > 10*eavg[_nb]
		mainfigaxis.plot(mavg[_nb][mask],mstd[_nb][mask],'bo')
		if len(uobj[mask])>0:
			print uobj[mask]

	py.show()

################################################################################

if __name__ == '__main__':

	main(sys.argv)

################################################################################