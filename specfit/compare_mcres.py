#! /usr/bin/env python

import os,sys
import numpy as np
import pylab as py
import logging as log
#import pymc
from astropy.table import Table

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
	
	ax1 = py.subplot(221)
	ax2 = py.subplot(222)
	ax3 = py.subplot(223)
	ax4 = py.subplot(224)
	
	for csv in args[1:]:
		log.info('Reading in %s...'%(csv))
		data = Table.read(csv,format='ascii')
		try:
			ax1.errorbar(data['Mean'][0],data['Mean'][1],data['MC Error'][0],data['MC Error'][1],fmt='b.')
			ax2.errorbar(data['Mean'][2],data['Mean'][3],data['MC Error'][2],data['MC Error'][3],fmt='b.')
			ax3.errorbar(data['Mean'][4],data['Mean'][5],data['MC Error'][4],data['MC Error'][5],fmt='b.')
			ax4.errorbar(data['Mean'][7],data['Mean'][8],data['MC Error'][7],data['MC Error'][8],fmt='b.')
		except:
			pass

	py.show()
	#py.xlim(-1,45)
	#py.ylim(-1,12)
	py.show()

################################################################################


if __name__ == "__main__":

	main(sys.argv)

################################################################################