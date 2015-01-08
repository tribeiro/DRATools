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
	
	parser.add_option('-f','--filename',
					  help = 'Input spectrum to fit.'
					  ,type='string')

	opt,args = parser.parse_args(argv)

	llist = np.loadtxt(opt.filename,dtype='S',unpack=True)
	
	dtype = [('scale', '<f8'), ('velocity', '<f8'),
	 ('temp1', '<i4') , ('temp2', '<i4')]

	hist = np.zeros(131*21).reshape(131,21)
	
	ax1 = py.subplot(221)
	ax2 = py.subplot(222)
	ax3 = py.subplot(223)
	ax4 = py.subplot(224)

	for i,l in enumerate(llist[0]):

		csvlist = np.loadtxt(l,dtype='S')

		for csv in csvlist:
			log.info('Reading in %s...'%(csv))
			try:
				data = Table.read(csv,format='ascii')
				ax1.errorbar(data['Mean'][0],data['Mean'][1],data['MC Error'][0],data['MC Error'][1],fmt=llist[1][i])
				ax2.errorbar(data['Mean'][2],data['Mean'][3],data['MC Error'][2],data['MC Error'][3],fmt=llist[1][i])
				ax3.errorbar(data['Mean'][4],data['Mean'][5],data['MC Error'][4],data['MC Error'][5],fmt=llist[1][i])
				ax4.errorbar(data['Mean'][6],data['Mean'][7],data['MC Error'][6],data['MC Error'][7],fmt=llist[1][i])
			except:
				log.exception(sys.exc_info())
				pass

	py.show()
	#py.xlim(-1,45)
	#py.ylim(-1,12)
	py.show()

################################################################################


if __name__ == "__main__":

	main(sys.argv)

################################################################################