import sys,os
import numpy as np
import pylab as py
from astropy.table import Table
import logging

################################################################################

def main(argv):
	
	logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
						level=logging.INFO)

	path = '/Volumes/TiagoHD2/Documents/specfit/'
	path = os.path.expanduser('~/Downloads')
	hdf5 = 'snr_calc.hdf5'
	tablist = 'specfit.lis'


	tabl = np.loadtxt(os.path.join(path,tablist),dtype='S')

	data = np.array(np.zeros(len(tabl)),
					dtype=[('blue',np.float),
						   ('mid',np.float),
						   ('red',np.float)])

	for i in range(len(tabl)):
		logging.info(tabl[i])
		snr = Table.read(os.path.join(path,hdf5),path=tabl[i])
		data[i]['blue'] = snr['blue'][0]
		data[i]['mid'] = snr['mid'][0]
		data[i]['red'] = snr['red'][0]

	xbins1 = np.linspace(0,50,50)
	xbins2 = np.linspace(0,150,150)
	xbins3 = np.linspace(0,150,150)

	py.subplot(311)
	py.hist(data['blue'],bins=xbins1)#,normed=True,stacked=True)
	py.xlim(0,300)

	py.subplot(312)
	py.hist(data['mid'],bins=xbins2)#,normed=True,stacked=True)
	py.xlim(0,300)

	py.subplot(313)
	py.hist(data['red'],bins=xbins3)#,normed=True,stacked=True)
	py.xlim(0,300)

	py.show()

################################################################################

if __name__ == '__main__':

	main(sys.argv)

################################################################################