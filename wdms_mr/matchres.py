#!/usr/bin/env python

import sys,os
import numpy as np
import pylab as py
from astropy.table import Table
import logging as log
from progrid import *

'''
@help: Comparison of results from specfitMC.py run and those of 
Rebassa-Mansergas et al (2012). For the templates it will translate from index
to parameter values.

@author: Tiago Ribeiro de Souza
@date: 11/11/2014
'''

################################################################################

def main(argv):
	
	log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
					level=log.INFO)

	############################################################################
	# Basic path, file and information definitions
	#
	_path1 = '/Volumes/TiagoHD2/Documents/data/'
	_path2 = '/Volumes/TiagoHD2/Documents/specfit/'
	
	# stores the results of RM12
	_file1 = 'wdms.fits'
	
	# List of files with results from specfit to compare
	_list2 = 'specfit_csv_res.lis'

	# Grid list used to run specfitMC.py
	_tgrids = 'grid.lis'

	# output file
	output = 'snr_matchres_csv.hdf5'
	
	#
	mjd_id = 'MJD'   # MJD   table column name
	plate_id = 'PLT' # Plate table column name
	fiber_id = 'FIB' # Fiber table column name
	#
	############################################################################
	# Read data
	
	# From RM12
	rm12 = os.path.join(_path1,_file1)
	log.info('Reading in RM12 data from %s'%(rm12))
	rm12_hdu = Table.read(rm12)

	# From csv list of files generated by specfit
	log.info('Reading list of csv file from %s'%(_list2))
	csv_list = Table.read(os.path.join(_path2,_list2),format='ascii.no_header')
	log.info('%i entries to be processed...'%(len(csv_list)))
	
	# Template Grids
	log.info('Reading list of template grids from %s'%(_tgrids))
	grid_list = Table.read(os.path.join(_path2,_tgrids),
						   format='ascii.no_header')
	
	grid1 = WDgrid(os.path.join(_path2,grid_list['col1'][0]))
	grid2 = MDgrid(os.path.join(_path2,grid_list['col1'][1]))
	
	############################################################################
	# Create arrays to store information
	
	data = np.array(np.zeros(len(csv_list)),
					dtype=[('scale_0', '<f8'), ('velocity_0', '<f8'),
						   ('scale_1', '<f8'), ('velocity_1', '<f8'),
						   ('Teff_1', '<f8') , ('logg_1', '<f8'),
						   ('Teff_2', '<f8') , ('logg_2', '<f8'),
						   ('m_2','<f8'),
						   ('template_0', '<i4') , ('template_1', '<i4'),
						   ('template_2', '<i4') , ('template_3', '<i4'),
						   ('template_4', '<i4') , ('sig', '<f8')])

	err = np.array(data)
	
	xmtype = [('TRidx','<i4'),('RM12idx','<i4'),
			  ('nsol','<i4'),('sol','<i4'),
			  ('TRspecfile','S20'),('Plate','<i4'),
			  ('MJD','<i4'),('Fiber','<i4')]
	# match cannot be larger than rm12 file, can be smaller though... :-(
	# -1 will flag empty entries...
	xmatch = np.array(np.zeros(len(rm12_hdu))-1,dtype=xmtype)
	
	idx_vec = np.arange(len(rm12_hdu))
	
	############################################################################
	# Processing
	log.info('Processing...')
	for i,csv_file in enumerate(csv_list['col1']):
		log.debug('%4i/%4i Reading %s:'%(i+1,len(data),csv_file))
		# Take mjd,plate,fiber from file name
		plate,mjd,fiber = np.array(csv_file.split('.csv')[0].split('-')[1:],
								   dtype=float)
		# match with information from RM12
		mask = np.bitwise_and(np.bitwise_and(rm12_hdu[mjd_id] == mjd,
											 rm12_hdu[plate_id]==plate),
							  rm12_hdu[fiber_id]==fiber)
		idx = np.array(idx_vec[mask])
		#print idx

		if len(idx) == 0:
			log.warning('No match found for spectra %s'%(csv_file))
	
		for jj in idx:
			xmatch['TRidx'][jj] = i
			xmatch['RM12idx'][jj] = jj
			xmatch['nsol'][jj] = len(idx)
			xmatch['sol'][jj] = rm12_hdu['sol'][jj]
			xmatch['TRspecfile'][jj] = os.path.basename(csv_file)
			xmatch['Plate'][jj] = plate
			xmatch['MJD'][jj] = mjd
			xmatch['Fiber'][jj] = fiber
		
		# Get my solution from csv file
		csv_data = Table.read(os.path.join(_path2,csv_file))
		for j,par in enumerate(csv_data['Parameter']):
			data[par][i] = csv_data['Mean'][j]
			err[par][i] = csv_data['MC Error'][j]
		
		data['Teff_1'][i] = grid1.Teff(csv_data['Mean'][4])
		data['logg_1'][i] = grid1.logg(csv_data['Mean'][5])

		data['m_2'][i]    = grid2.metal(csv_data['Mean'][6])
		data['Teff_2'][i] = grid2.Teff(csv_data['Mean'][7])
		data['logg_2'][i] = grid2.logg(csv_data['Mean'][8])

			
	############################################################################
	# Saving: Will create an astropy.table object for each table and save them
	# to an hdf5 file.
	
	# creating table with xmatch infor
	tableData = Table(data,meta={'info':'Table with final parameters values.'})
	tableErr = Table(err,meta={'info':'Table with final parameters error.'})
	tableXmatch = Table(xmatch,meta={'info':'Table with match information.'})
	
	outname = os.path.join(_path2,output)
	
	log.info('Writing output to %s'%(outname))
	
	log.info('Saving xmatch..')
	
	tableXmatch.write(outname,
					  format='hdf5',
					  path='xmatch',append=False)

	log.info('Saving data...')
	
	tableData.write(outname,
					format='hdf5',
					path='data',append=True)

	log.info('Saving err...')
	
	tableErr.write(outname,
				   format='hdf5',
				   path='err',append=True)
	
	log.info('Saving RM12...')
	
	rm12_hdu.write(outname,
				   format='hdf5',
				   path='RM12',append=True)

	log.info('Done')
	
	return 0
################################################################################

if __name__ == '__main__':
	
	main(sys.argv)

################################################################################