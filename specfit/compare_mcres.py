#! /usr/bin/env python

import os,sys
import numpy as np
import pylab as py
import logging as log
import pymc

################################################################################

def main(argv):

	log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
					level=log.INFO)

	from optparse import OptionParser
    
	parser = OptionParser()

	opt,args = parser.parse_args(argv)

	dtype = [('scale', '<f8'), ('velocity', '<f8'),
	 ('temp1', '<i4') , ('temp2', '<i4')]

	hist = np.zeros(131*21).reshape(131,21)
	
	for pickle in args[1:]:
		log.info('Reading in %s...'%(pickle))
		db = pymc.database.pickle.load(pickle)
		oarray = np.zeros(len(db.trace('scale')[:]),
						  dtype=dtype)
		oarray['scale'] = np.array(	[i[0] for i in db.trace('scale')[:]] )
		oarray['velocity'] = np.array(	[i[0] for i in db.trace('velocity')[:]] )
		oarray['temp1'] = np.array(	[i[0] for i in db.trace('template')[:]] )
		oarray['temp2'] = np.array(	[i[1] for i in db.trace('template')[:]] )
		h2d,xx,yy = np.histogram2d(oarray['temp1'],oarray['temp2'],
								   bins=( np.arange(-1,131) , np.arange(-1,21)))
		hist += h2d
		#py.plot(oarray['temp1'],oarray['temp2'],'.')

	py.imshow(hist,
			  interpolation='nearest',
			  aspect='auto',
			  origin='lower')
	#py.xlim(-1,45)
	#py.ylim(-1,12)
	py.show()

################################################################################


if __name__ == "__main__":

	main(sys.argv)

################################################################################