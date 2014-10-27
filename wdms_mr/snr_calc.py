#!/usr/bin/env python

import sys,os
import numpy as np
from astropy.table import Table
import logging

################################################################################

def main(argv):

	logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
						level=logging.INFO)

	from optparse import OptionParser

	parser = OptionParser()

	parser.add_option('-f','--filename',
					help = 'Input spectrum to fit.'
					,type='string')
	parser.add_option('-o','--output',
					  help = 'Output root name.'
					  ,type='string')
	parser.add_option('-v','--verbose',
					  help = 'Run in verbose mode.',action='store_true',
					  default=False)

	opt,args = parser.parse_args(argv)

	snr_windows = np.array([(4000,4500,'blue'),
							(6250,6750,'mid'),
							(8070,8280,'red')],
						   dtype=[('start', '<f8'),
								  ('end', '<f8'),
								  ('name','S5')])

	snr_avg = np.zeros(len(snr_windows))

	spec = Table.read(opt.filename,hdu=1)
	wave = 10**spec['loglam']
	snr = spec['flux']*spec['ivar']
	
	for i in range(len(snr_avg)):
		mask = np.bitwise_and(wave > snr_windows['start'][i],
							  wave < snr_windows['end'][i])
		snr_avg[i] = np.mean(snr[mask])

	t = Table(np.array([snr_avg]),names=tuple(snr_windows['name']))

	t.write(opt.output,format='hdf5',path=opt.filename,append=True)

	return 0

################################################################################

if __name__ == '__main__':

	main(sys.argv)