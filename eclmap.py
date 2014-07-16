#! /usr/bin/env python

'''
	Show CAL 87 light curves for analysis purposes. 
	
	c - Tiago Ribeiro 16/12/2014
'''

import os,sys
import numpy as np
import pylab as py
import matplotlib.cm as cm
from matplotlib.ticker import MaxNLocator
from optparse import OptionParser
from eclmapF import *

######################################################################

def main(argv):

	##################################################################
	# Parse arguments

	dsetoptions = {0:'0305',1:'031',2:'051',3:'0514'}
	figtitle = {0:'Soft (0.3 - 0.5 keV)',
				1:'031',
				2:'Hard (0.5 - 1.0 keV)',
				3:'Hard (0.5 - 1.4 keV)'}
	rcirc = 0.191
	vmin = [ {0:-5.5,10:-5.42, 11:-5.13,12:-5.37, 13:-5.13, 15:-5.44},
			 {1:-5.1},
			 {0:-5.13,1:-5.36},
			 {0:-5.13,1:-5.36} ]
	vmax = [ {0:-4.7,10:-4.92, 11:-4.57,12:-4.87,13:-4.57, 15:-4.54},
			 {1:-5.0},
			 {0:-4.63,1:-4.86},
			 {0:-4.63,1:-4.86} ]
	ymin = [0,0,0,0]
	ymax = [2,4,2,2]
	
	from optparse import OptionParser
	
	parser = OptionParser()
	
	parser.add_option(	'--dataset',
						help='One of the following options %r.'%dsetoptions,
						type='int')

	parser.add_option(	'--parset',
						help='Parameter set.',
						type='int')

	parser.add_option('-s','--savefig',
			  help = 'Save resulting figure. Will be stores in default file.',action='store_true',default=False)

	opt,args = parser.parse_args(argv)

	print 'Running on %s[%i] dataset...'%(dsetoptions[opt.dataset],opt.dataset)
	##################################################################
	# Input definition
	_path = os.path.expanduser('/Volumes/TiagoHD2/analise/CAL87/emap_%skeV_rateall/par%02i'%(dsetoptions[opt.dataset],opt.parset))
	_opath = os.path.expanduser('~/Dropbox/Documents/paper_cal87/Figures')
	_oname = 'cal87_%skeV_rateall.pdf'%(dsetoptions[opt.dataset])
	_cldat = 'cal87_%skeV_rateall.dat.61'%(dsetoptions[opt.dataset]) #'cal87_0305keV_rateall.dat.122'
	_clmod = 'cal87_%skeV_rateall.prd.61'%(dsetoptions[opt.dataset])
	_emap = 'cal87_%skeV_rateall.mem.51'%(dsetoptions[opt.dataset])
	_mrad = 'cal87_%skeV_rateall.rad.51'%(dsetoptions[opt.dataset])
	
	#_cldat = 'cal87_%skeV_caixas.dat.58'%(dsetoptions[opt.dataset]) #'cal87_0305keV_rateall.dat.122'
	#_clmod = 'cal87_%skeV_caixas.prd.58'%(dsetoptions[opt.dataset])
	#_emap = 'cal87_%skeV_caixas.mem.51'%(dsetoptions[opt.dataset])

	_lobr = 'lob.dat'
	_tbal = '../../trajbal.dat'
	#
	##################################################################
	# Reading data
	
	cldat = np.loadtxt(os.path.join(_path,_cldat),unpack=True)
	clmod = np.loadtxt(os.path.join(_path,_clmod),unpack=True)
	map = read_mem(os.path.join(_path,_emap))
	rad = np.loadtxt(os.path.join(_path,_mrad),unpack=True)
	lobr = np.loadtxt(os.path.join(_path,_lobr),unpack=True)
	tbal = np.loadtxt(os.path.join(_path,_tbal),unpack=True)
	#
	##################################################################
	# Plotting map
	
	py.figure(1)#,figsize=(4,8))
	
	##################################################################
	
	py.subplot(122)
	
	print '# ECLIPSE MAP: MIN(%.2f) MAX(%.2f)'%(np.min(np.log10(map)),np.max(np.log10(map)))


	py.imshow(	np.log10(map),
				interpolation='nearest',
				origin='lower',
				vmin=vmin[opt.dataset][opt.parset-1],
				vmax=vmax[opt.dataset][opt.parset-1],
				cmap=cm.gray_r,
				extent=[-1.0,1.0,-1.0,1.0])
	py.plot([0],[0],'w+')
	py.plot(lobr[0],lobr[1],'k:')
	py.plot(lobr[0],-lobr[1],'k:')
	py.plot(tbal[1],tbal[2],'k:')
	theta = np.linspace(0,2.*np.pi,100)
	xx = rcirc*np.sin(theta)
	yy = rcirc*np.cos(theta)
	py.plot(xx,yy,'k:')
	py.xlim(-1,1)
	py.ylim(-1,1)

	py.xlabel('$x/R_{L1}$',size=20)
	py.ylabel('$y/R_{L1}$',size=20)

	py.title('Eclipse map',size=20)

	##################################################################
	
	ax2 = py.subplot(121)#,aspect=0.4/2, adjustable='box')
	
	py.errorbar(cldat[0],cldat[1],cldat[2],fmt='r_',capsize=0)
	py.plot(clmod[0],clmod[1],'k-')
				
	ax2.xaxis.set_major_locator(MaxNLocator(5))
	py.xlim(-0.2,0.2)

	py.ylim(ymin[opt.dataset],ymax[opt.dataset])
	
	py.xlabel('Orbital Phase',size=20)
	py.ylabel('Count rate',size=20)
	py.title(figtitle[opt.dataset],size=20)
	
	##################################################################
			
	#ax3 = py.subplot(313,aspect=2.1/3)
	
	#py.plot(np.log10(rad[0]),np.log10(rad[3]),'.')

	#py.ylim(vmin[opt.dataset][opt.parset-1],
	#		vmax[opt.dataset][opt.parset-1])
	#py.xlim(-2,0.1)

	#
	##################################################################
	# End
	
	#py.subplots_adjust(wspace=0.25)
	
	if opt.savefig:
		print '# - Saving figure @: %s'%(os.path.join(_opath,_oname))
		py.savefig(os.path.join(_opath,_oname))
	py.show()
	
	return 0

######################################################################

if __name__ == '__main__':

	main(sys.argv)

######################################################################