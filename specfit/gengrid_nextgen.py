#! /usr/bin/env python

'''
	Generate grid for next-gen models.
'''

import sys,os
import numpy as np
import logging as log

def main(argv):

	log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
						level=log.DEBUG)

	from optparse import OptionParser

	parser = OptionParser()

	parser.add_option('-o','--output',
					  help = 'Output grid list.'
					  ,type='string')

	opt,args = parser.parse_args(argv)

	_path = '/Volumes/TiagoHD2/Documents/SpecLibrary/'
	_file = 'BT-NextGen.lis'

	ndim = 3

	grid = np.loadtxt(os.path.join(_path,_file),dtype='S',unpack=True)

	grid = np.array([os.path.basename(g) for g in grid])
	rootname = 'lte%03i%+4.1f%s.BT-NextGen.7.bz2'

	teff = np.arange(26,71,1)
	logg = np.arange(0.,5.5,0.5)
	mhalpha = [ '-0.0a+0.0',
				'+0.3a+0.0',
				'+0.5a+0.0',
				'-0.5a+0.2',
				'-1.0a+0.4',
				'-1.5a+0.4']
	nfail = 0
	nfiles = 0

	outlits = np.array(np.zeros(len(teff)*len(logg)*len(mhalpha)),
						dtype = [('fname', '<S36'), ('it','<i4'),
								 ('il','<i4'),('imh','<i4')])
								   
	for it,t in enumerate(teff):
		for il,l in enumerate(logg):
			for imh,mh in enumerate(mhalpha):
				
				fname = rootname%(t,-l,mh)
				outlits[nfiles]['fname'] = fname
				outlits[nfiles]['it'] = it
				outlits[nfiles]['il'] = il
				outlits[nfiles]['imh'] = imh
				nfiles += 1

				if not fname in grid:
					nfail += 1
					log.info('%s [FAIL]'%fname)
				else:
					log.info('%s %3i %3i %3i'%(fname,it,il,imh))

	if opt.output:
		log.info('Saving grid list to %s...'%opt.output)
		np.savetxt(opt.output,X=outlits,fmt="%s %3i %3i %3i")

	log.info('Failed to find %i of %i files...'%(nfail,nfiles))

if __name__ == '__main__':

	main(sys.argv)