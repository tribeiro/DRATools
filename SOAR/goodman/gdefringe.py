#!/usr/bin/env python

'''

Created on 05/29/2012 - Tiago Ribeiro

'''

import sys
from pyraf import iraf
from pyraf.iraf import pysoar
import soarprint

import gdefringeF

def main(argv):

	from optparse import OptionParser
	
	parser = OptionParser()
	
	parser.add_option('-i','--images',
			  help = 'List of input images.',type='string')
	parser.add_option('-f','--fringe',
			  help = 'List of fringe images. One image or a list with the same size of input.'
			  ,type='string')
	parser.add_option('-o','--output',
			  help = 'List of output images. If none given will attach .dfringe to end of file name (before .fits).',type='string')
	parser.add_option('-n','--noproc',
			  help = 'List results only?',action='store_true',default=False)
	parser.add_option('--wcorr_size',
			  help = 'Window size in angstroms of portion of spectrum to correlate. If INDEF, use entire wavelength overlap between template and spectrum. default="120".'
			  ,default='120',type='string')
	parser.add_option('--wcorr_dist_from_end',
			  help = 'How far from the end of the spectrum in angstroms should the correlation window end. If INDEF, use end of wavelength overlap between template and spectrum. default="20".'
			  ,default='20',type='string')
	parser.add_option('--niter',
			  help = 'How many iterations for the scaling algorith (default = 1).'
			  ,default=1,type=int)
	parser.add_option('--sigma',
			  help = 'Sigma clipping for the scaling algorith iterations (default = 3).'
			  ,default=3.0,type=int)
	parser.add_option('--logfile',
			  help = 'Logfile.',type='string',default='gdefringe.log')
	parser.add_option('-v','--verbose',
			  help = 'Run in verbose mode.',action='store_true',default=False)

	opt,args = parser.parse_args(argv)
	
	#gdf = gdefringeF.gdefringe(opt.images,opt.fringe,opt.output,opt.noproc,opt.st_lambda,opt.end_lambda,opt.verbose)
	gdf = gdefringeF.gdefringe(opt)

	gdf.defringe()
	
	
if __name__ == '__main__':

	main(sys.argv)
	
