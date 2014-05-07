#! /usr/bin/env python

'''
	Show CAL 87 eclipse mapping results. Figure for paper. 
	
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

	dsetoptions = {0:'0305',2:'0514'}
	figtitle = {0:'Soft (0.3 - 0.5 keV)',1:'031',2:'Hard (0.5 - 1.4 keV)'}
	rcirc = 0.191
	vmin = [ {0:-5.5, 11:-5.13, 12:-5.21,14:-5.21},{1:-5.1},{0:-5.21} ]
	vmax = [ {0:-4.7, 11:-4.49, 12:-4.70,14:-4.70},{1:-5.0},{0:-4.70} ]
	ymin = [0.01,0,0.0]
	ymax = [2.01,4,2.0]
	
	from optparse import OptionParser
	
	parser = OptionParser()
	parser.add_option('-s','--savefig',
			  help = 'Save resulting figure. Will be stores in default file.',action='store_true',default=False)

	opt,args = parser.parse_args(argv)
	
	dataset = 0
	parset = 12

	_lobr = 'lob.dat'
	_tbal = '../../trajbal.dat'

	#
	##################################################################
	# Plotting

	py.figure(1,figsize=(10,5))
	
	#
	##################################################################
	# Reading data
	
	for dataset in [0,2]:
		if dataset == 0:
			parset = 13
			col = 0
		else:
			col = 1
			parset = 1
			
		##################################################################
		# Input definition
		_path = os.path.expanduser('~/Documents/analise/CAL87/emap_%skeV_rateall/par%02i'%(dsetoptions[dataset],parset))
		_opath = os.path.expanduser('~/Dropbox/Documents/paper_cal87/Figures')
		_oname = 'cal87_rateall.eps'
		_cldat = 'cal87_%skeV_rateall.dat.122'%(dsetoptions[dataset]) #'cal87_0305keV_rateall.dat.122'
		_clmod = 'cal87_%skeV_rateall.prd.122'%(dsetoptions[dataset])
		_emap = 'cal87_%skeV_rateall.mem.51'%(dsetoptions[dataset])
		_mrad = 'cal87_%skeV_rateall.rad.51'%(dsetoptions[dataset])

		cldat = np.loadtxt(os.path.join(_path,_cldat),unpack=True)
		clmod = np.loadtxt(os.path.join(_path,_clmod),unpack=True)
		map = read_mem(os.path.join(_path,_emap))
		rad = np.loadtxt(os.path.join(_path,_mrad),unpack=True)
		lobr = np.loadtxt(os.path.join(_path,_lobr),unpack=True)
		tbal = np.loadtxt(os.path.join(_path,_tbal),unpack=True)
		

		
		##################################################################
		
		ax1 = py.subplot(2,3,2+3*col)
		
		print '# ECLIPSE MAP: MIN(%.2f) MAX(%.2f)'%(np.min(np.log10(map)),np.max(np.log10(map)))


		py.imshow(	np.log10(map),
					interpolation='nearest',
					origin='lower',
					vmin=vmin[dataset][parset-1],
					vmax=vmax[dataset][parset-1],
					cmap=cm.gray_r,
					extent=[-1.0,1.0,-1.0,1.0])
		py.plot([0],[0],'w+')
		py.plot(lobr[0],lobr[1],'k-',alpha=0.5)
		py.plot(lobr[0],-lobr[1],'k-',alpha=0.5)
		py.plot(tbal[1],tbal[2],'k--',alpha=0.5)
		theta = np.linspace(0,2.*np.pi,100)
		xx = rcirc*np.sin(theta)
		yy = rcirc*np.cos(theta)
		py.plot(xx,yy,'w:')
		py.xlim(-1,1)
		py.ylim(-1,1)

		#py.xlabel('$x/R_{L1}$',size=20)
		py.ylabel('$y/R_{L1}$')#,size=20)

		#py.title('Eclipse map',size=20)

		##################################################################
		
		ax2 = py.subplot(2,3,1+3*col,aspect=0.4/2, adjustable='box')
		
		py.errorbar(cldat[0],cldat[1],cldat[2],fmt='r.',capsize=0)
		py.plot(clmod[0],clmod[1],'k-')
					
		ax2.xaxis.set_major_locator(MaxNLocator(5))
		py.xlim(-0.2,0.2)

		py.ylim(ymin[dataset],ymax[dataset])
		
		#py.xlabel('Orbital Phase',size=20)
		py.ylabel('Count rate')#,size=20)
		#py.title(figtitle[dataset],size=20)
		
		##################################################################
				
		ax3 = py.subplot(2,3,3+3*col,aspect=2.1/1.99)
		
		mask = rad[0] < 0.5
		
		py.plot(np.log10(rad[0][mask]),np.log10(rad[3][mask]),'.')
		#ax3.set_yscale('log')
		#ax3.set_xscale('log')
		
		py.ylabel('$\\log_{10}(I_\\nu$)')

		py.ylim(-6,-4.01)
		py.xlim(-2,0.1)

		if dataset == 0:
			py.setp(ax1.get_xticklabels(),visible=False)
			py.setp(ax2.get_xticklabels(),visible=False)
			py.setp(ax3.get_xticklabels(),visible=False)
		else:
			ax1.arrow(0.75, 0.75, -0.2, -0.2, head_width=0.05, head_length=0.1, fc='k', ec='k')
			ax2.set_xlabel('Orbital Phase')
			ax1.set_xlabel('$x/R_{L1}$')
			ax3.set_xlabel('$\\log_{10}(r/R_{L1})$')

		ax3.annotate(figtitle[dataset], rotation=-90, xy=(1.1, .5),  xycoords='axes fraction',
                horizontalalignment='center', verticalalignment='center')
	#
	##################################################################
	# End
	
	py.subplots_adjust(hspace=0.,right=0.95,left=0.05,bottom=0.12,top=0.95)
	
	if opt.savefig:
		print '# - Saving figure @: %s'%(os.path.join(_opath,_oname))
		py.savefig(os.path.join(_opath,_oname))
	py.show()
	
	return 0

######################################################################

if __name__ == '__main__':

	main(sys.argv)

######################################################################