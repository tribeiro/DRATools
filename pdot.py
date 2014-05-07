#! /usr/bin/env python

'''
	Calculates Pdot for a O-C time of eclipses, considering Pdot constant over time.
'''

import sys,os
import numpy as np
import pylab as py

######################################################################

def main(argv):
	'''
Main function. Reads input parameters and run iteractive procedure. 
Run with -h to get help on input parameters.

Defaults to CAL87 data on ribeiro & lopes de oliveira (2014)
	'''

	from optparse import OptionParser
	
	parser = OptionParser()
	
	parser.add_option(	'--HJD0',
						help='Reference time of first eclipse in\
						 HJD. Ephemeris.',
						type='float',
						default=2450111.5144)
	parser.add_option(	'--P0',
						help='Reference orbital period in days.',
						type='float',
						default=0.44267714)
	parser.add_option(	'--DT0',
						help='Measured difference between observed\
						 and calculated eclipse time.',
						type='float',
						default=0.)
	parser.add_option(	'--E',
						help='Number of observed cycle, with \
						respect to HJD0, the reference first\
						 eclipse.',
						type='float',
						default=5997)
	parser.add_option(	'--sigmaDT0',
						help='Uncertainty in the determination\
						 of DT0.',
						type='float',
						default=0.)

	opt,args = parser.parse_args(argv)

	print '''
PDOT.PY -	calculates Pdot for given O-C between eclipses,
			considers Pdot is constant.

c - Tiago Ribeiro - UFS - 2013
'''

	print 'HJD0 = %f'%opt.HJD0
	print 'P0 = %f'%opt.P0
	print 'DT0 = %f'%opt.DT0
	print 'E = %f'%opt.E

	# First iteration. Considers T0' = T0 to obtain DT
	DT = opt.P0 * opt.E # Calculated time of eclipse
	Pdot = opt.DT0 / DT / opt.E # calculated Pdot

	print 'Pdot = %e'%(Pdot)

	difPdot = 1.0

	print '---------------------------------------------------'
	print '|Pdot          | difPdot          | relDif        |'
	while (difPdot/Pdot > 1e-10):
		DT = opt.P0 * opt.E + Pdot * DT * opt.E # Calculated time of eclipse
		oldPdot = Pdot
		Pdot = opt.DT0 / DT / opt.E # calculated Pdot
		difPdot = np.abs(Pdot - oldPdot)
		
		print '|%14.8e|%18.10e|%15.8e|'%(Pdot,difPdot,difPdot/Pdot)
	print '---------------------------------------------------'

	if opt.sigmaDT0 > 0:
		sDT0 = opt.sigmaDT0
		sigmaPdot = np.sqrt( (sDT0 / opt.E / DT)**2. + (sDT0 * opt.DT0 / opt.E / DT**2.)**2. )
		print 'Pdot = %e +/- %e'%(Pdot,sigmaPdot)
	else:
		print 'Pdot = %e'%(Pdot)
######################################################################

if __name__ == '__main__':

	main(sys.argv)

######################################################################