#! /usr/bin/env python

'''
	Show CAL 87 xray spectra as a trailed spectrogram. 
	
	c - Tiago Ribeiro 16/12/2014
'''

import os,sys
import numpy as np
import pylab as py
import matplotlib.cm as cm
import pyfits
from astropysics import spec,utils

######################################################################

def main(argv):

	from optparse import OptionParser
	
	parser = OptionParser()
	parser.add_option('-s','--savefig',
			  help = 'Save resulting figure. Will be stored in default file.',action='store_true',default=False)

	opt,args = parser.parse_args(argv)

	_path = os.path.expanduser('~/Documents/analise/CAL87/spec/')
	_splist = 'spec.lis'

	_cl = '../cal87_TTERRA_allbands.tfits'
		
	w1 = 24.5 #18.5 #18.5
	w2 = 25.2 #19.5 #19.5

	w1 = 18.5 #18.5
	w2 = 24.5 #19.5

	w1 = 18.5
	w2 = 19.5
		
	splist = np.loadtxt(os.path.join(_path,_splist),
						dtype='S',
						unpack=True)

	cluz = pyfits.getdata(os.path.join(_path,_cl))
	
	# Use first spectrum as template
	sptemplate = pyfits.getdata(splist[0][0])
	wmask = np.bitwise_and(sptemplate['CHANNEL']> w1, sptemplate['CHANNEL'] < w2)
	spdat = np.array([])

	for i in range(len(splist[0])):
		print '# - [%i/%i] Working on %s ...'%(i,len(splist[0]),splist[0][i])
		sp = pyfits.getdata(splist[0][i])
		mask = np.isnan(sp['FLUX'])
		sp['FLUX'][mask] = 0.
		aspec = spec.Spectrum(	sp['CHANNEL'],
								sp['FLUX'])
		if not aspec.isXMatched(sptemplate['CHANNEL']):
			ospec = aspec.resample(sptemplate['CHANNEL'][wmask])
			spdat = np.append(spdat,ospec[1])
		else:
			spdat = np.append(spdat,aspec.flux[wmask])

	spdat = spdat.reshape(len(splist[0]),-1)

	fig = py.figure(1)

	ax1 = fig.add_axes([0.2,0.1,0.65,0.75]) # main figure
	
	#py.subplot(121)
	splist1 = np.array(splist[1],dtype=float)-float(splist[1][0])
	splist2 = np.array(splist[2],dtype=float)-float(splist[1][0])
	cltime = (cluz['TIME']-float(splist[1][0]))/86400.
	#cltime = (cluz['TIME']-cluz['TIME'][0])/86400.

	splist1 /= 86400.
	splist2 /= 86400.

	print [w1,w2,splist1[0],splist2[-1]],cltime[0]

	mask = spdat>0
	min = np.min(spdat[mask])
	spdat[np.bitwise_not(mask)]=min
	print min

	itrp = 'bicubic'
	itrp = 'nearest'
	#itrp = 'sinc'
	ax1.imshow(spdat,
				aspect='auto',
				interpolation=itrp,
				filterrad=.5,
				cmap=cm.gray_r,
				origin='lower',
				extent=[w1,w2,splist1[0],splist2[-1]])
	#py.plot([w1,w2],[0.5,.5],'k:')
	#py.plot([w1,w2],[1.5,1.5],'k:')
	ax1.plot([w1,w2],[splist1[3],splist1[3]],'k:')
	ax1.plot([w1,w2],[splist1[6],splist1[6]],'k:')

	ax1.plot([w1,w2],[splist1[16],splist1[16]],'k:')
	ax1.plot([w1,w2],[splist1[19],splist1[19]],'k:')

	ax1.set_xlim(w1,w2)
	ax1.set_ylim(splist1[0],splist2[-1])
	py.setp(ax1.get_yticklabels(),visible=False)
	
	#py.subplot(122)

	ax3 = fig.add_axes([0.85,0.1,0.1,0.75])

	ax3.errorbar(-cluz['RATIO_0510305'],cltime,xerr=cluz['ERROR_0510305'],fmt='.')
	
	ylim = ax3.get_ylim()
	ax3.plot([-1.0,-1.0],ylim,'k--')
	ax3.plot([-1.25,-1.25],ylim,'k--')
	ax3.plot([-1.5,-1.5],ylim,'k--')
		
	ax4 = fig.add_axes([0.1,0.1,0.1,0.75])

	ax4.plot(-cluz['RATE_ALL031'],cltime,'.')
	
	a3xlim = ax3.get_xlim()
	a4xlim = ax4.get_xlim()
	
	for i in range(len(splist1)):
		if i in [3,4,5,6,16,17,18,19]:
			ax3.plot(a3xlim,[splist1[i],splist1[i]],'r:')
			ax4.plot(a4xlim,[splist1[i],splist1[i]],'r:')
		else:
			ax3.plot(a3xlim,[splist1[i],splist1[i]],'k:')
			ax4.plot(a4xlim,[splist1[i],splist1[i]],'k:')
	py.setp(ax3.get_xticklabels(),visible=False)
	py.setp(ax3.get_yticklabels(),visible=False)
	py.setp(ax4.get_xticklabels(),visible=False)

	ax3.set_ylim(splist1[0],splist2[-1])
	ax4.set_ylim(splist1[0],splist2[-1])

	ax3.set_xlim(*a3xlim)
	ax4.set_xlim(a4xlim[0]*1.05,a4xlim[1]*0.95)

	ax2 = fig.add_axes([0.2,0.85,0.65,0.1])
	
	spdat = spdat.T

	flux = np.zeros(len(spdat))
	
	for i in range(len(spdat)):
		flux[i] = np.mean(spdat[i])
	ax2.plot(sptemplate['CHANNEL'][wmask],flux,'-')
	py.setp(ax2.get_xticklabels(),visible=False)
	py.setp(ax2.get_yticklabels(),visible=False)
	ylim = ax2.get_ylim()
	ax2.set_ylim(ylim[0],ylim[1]*1.1)
	ax2.set_xlim(w1,w2)

	if opt.savefig:
		py.savefig('/Users/tiago/Dropbox/Documents/paper_cal87/Figures/trailedspec.pdf')
	py.show()


######################################################################

if __name__ == '__main__':

	main(sys.argv)