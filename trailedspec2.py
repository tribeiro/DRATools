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

def plotTrailer(sptemplate,spdat,w1,w2,splist1,splist2,ax):

	itrp = 'bicubic'
	itrp = 'nearest'
	#itrp = 'sinc'
	wmask = np.array([np.bitwise_and(sptemplate['CHANNEL']> w1, sptemplate['CHANNEL'] < w2)]*len(spdat))
	
	print spdat[wmask].reshape(len(spdat),-1).shape
	print wmask.shape
	ax.imshow(spdat[wmask].reshape(len(spdat),-1),
				aspect='auto',
				interpolation=itrp,
				filterrad=.5,
				cmap=cm.gray_r,
				origin='lower',
				extent=[w1,w2,splist1[0],splist2[-1]])
	#py.plot([w1,w2],[0.5,.5],'k:')
	#py.plot([w1,w2],[1.5,1.5],'k:')
	#ax.plot([w1,w2],[splist1[3],splist1[3]],'k:')
	#ax.plot([w1,w2],[splist1[6],splist1[6]],'k:')

	#ax.plot([w1,w2],[splist1[16],splist1[16]],'k:')
	#ax1.plot([w1,w2],[splist1[19],splist1[19]],'k:')

	ax.set_xlim(w1,w2)
	ax.set_ylim(splist1[0],splist2[-1])
	py.setp(ax.get_yticklabels(),visible=False)
	py.setp(ax.get_xticklabels(),rotation=45)

######################################################################

def plotCluz01(cltime,cluz,ax,markPeak=False):

	#ax.errorbar(-cluz['RATIO_0510305'],cltime,xerr=cluz['ERROR_0510305'],fmt='.')
	print cltime.shape,cluz.shape
	ax.plot(cltime,cluz,'.')
	ax.set_ylim(cltime[0],cltime[-1])
	ylim = ax.get_ylim()
	#ax.plot([-1.0,-1.0],ylim,'k--')
	#ax.plot([-1.25,-1.25],ylim,'k--')
	#ax.plot([-1.5,-1.5],ylim,'k--')
		
######################################################################

def plotSpec(spdat,sptemplate,w1,w2,ax,markPeak=False):

	spd = spdat.T

	flux = np.zeros(len(spd))
	
	for i in range(len(spd)):
		flux[i] = np.mean(spd[i])
	wmask = np.bitwise_and(sptemplate['CHANNEL']> w1, sptemplate['CHANNEL'] < w2)
	ax.plot(sptemplate['CHANNEL'][wmask],flux[wmask],'-')

	ylim = ax.get_ylim()
	if markPeak:
		imax = np.argmax(flux[wmask])
		x = sptemplate['CHANNEL'][wmask][imax]
		ax.plot([x,x],ylim,'k--')
		ax.plot([x-0.15,x-0.15],ylim,'k--')
		ax.plot([x+0.09,x+0.09],ylim,'k--')
		print x-0.15,x+0.09
				
	py.setp(ax.get_xticklabels(),visible=False)
	py.setp(ax.get_yticklabels(),visible=False)
	ax.set_ylim(ylim[0],ylim[1]*1.1)
	ax.set_xlim(w1,w2)

######################################################################

def getFlux(spdat,sptemplate,w1,w2):

	flux = np.zeros(len(spdat))
	
	for i in range(len(spdat)):
		flux[i] = np.mean(spdat)

	wmask = np.bitwise_and(sptemplate['CHANNEL']> w1, sptemplate['CHANNEL'] < w2)

	xx = sptemplate['CHANNEL'][wmask]
	for i in range(len(spdat)):
		yy = spdat[i][wmask]
		flux[i] = np.sum((xx[1:]-xx[:-1])*(yy[1:]+yy[:-1])/2.)

	return flux

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

	w1 = [24.3,18.70,14.0]
	w2 = [25.3,19.40,18.1]
		
	splist = np.loadtxt(os.path.join(_path,_splist),
						dtype='S',
						unpack=True)

	cluz = pyfits.getdata(os.path.join(_path,_cl))
	
	# Use first spectrum as template
	sptemplate = pyfits.getdata(splist[0][0])
	#wmask = np.bitwise_and(sptemplate['CHANNEL']> w1, sptemplate['CHANNEL'] < w2)
	spdat = np.array([])

	for i in range(len(splist[0])):
		print '# - [%i/%i] Working on %s ...'%(i,len(splist[0]),splist[0][i])
		sp = pyfits.getdata(splist[0][i])
		mask = np.isnan(sp['FLUX'])
		sp['FLUX'][mask] = 0.
		aspec = spec.Spectrum(	sp['CHANNEL'],
								sp['FLUX'])
		if not aspec.isXMatched(sptemplate['CHANNEL']):
			ospec = aspec.resample(sptemplate['CHANNEL'])
			spdat = np.append(spdat,ospec[1])
		else:
			spdat = np.append(spdat,aspec.flux)

	spdat = spdat.reshape(len(splist[0]),-1)

	fig = py.figure(1)

	ax = fig.add_axes([0,0,1,1])
	ax.axis("off")
	ax11 = fig.add_axes([0.2+0.3+0.175,0.12,0.175,0.75]) # main figure
	ax12 = fig.add_axes([0.2+0.3,0.12,0.175,0.75]) # main figure
	ax13 = fig.add_axes([0.2,0.12,0.3,0.75]) # main figure
		
	ax21 = fig.add_axes([0.2+0.3+0.175,0.87,0.175,0.1])
	ax22 = fig.add_axes([0.2+0.3,0.87,0.175,0.1])
	ax23 = fig.add_axes([0.2,0.87,0.3,0.1])

	ax3 = fig.add_axes([0.85,0.12,0.1,0.75])
		
	ax4 = fig.add_axes([0.1,0.12,0.1,0.75])
			
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
	print min, np.mean(spdat)

	plotTrailer(sptemplate,spdat,w1[0],w2[0],splist1,splist2,ax11)
	plotTrailer(sptemplate,spdat,w1[1],w2[1],splist1,splist2,ax12)
	plotTrailer(sptemplate,spdat,w1[2],w2[2],splist1,splist2,ax13)

	plotSpec(spdat,sptemplate,w1[0],w2[0],ax21)
	plotSpec(spdat,sptemplate,w1[1],w2[1],ax22)#,True)
	plotSpec(spdat,sptemplate,w1[2],w2[2],ax23)

	flx = getFlux(spdat,sptemplate,18.9,19.1)
	cflx1 = getFlux(spdat,sptemplate,18.9-0.2,18.9)
	cflx2 = getFlux(spdat,sptemplate,19.1,19.1+0.2)
	cflx = (cflx1+cflx2)/2.
	xx = np.zeros(len(splist1)*2)
	yy = np.zeros(len(splist1)*2)
	for i in range(len(splist1)):
		xx[i*2] = splist1[i]
		xx[i*2+1] = splist2[i]
		yy[i*2] = 1.-flx[i]/cflx[i]
		yy[i*2+1] = 1.-flx[i]/cflx[i]
	ax3.plot(yy,xx,ls='-')
	ax3.plot(1.-flx/cflx,(splist1+splist2)/2.,'.')
	#plotCluz01(splist1,flx,ax3)
	#py.subplot(122)

	ax4.plot(-cluz['RATE_ALL031'],cltime,'.')

	a3xlim = (-0.01,-5.0) #ax3.get_xlim()
	a4xlim = ax4.get_xlim()
	
	for i in range(len(splist1)):
		if i in [3,4,5,6,16,17,18,19]:
			ax3.plot(a3xlim,[splist1[i],splist1[i]],'r:')
			ax4.plot(a4xlim,[splist1[i],splist1[i]],'r:')
		else:
			ax3.plot(a3xlim,[splist1[i],splist1[i]],'k:')
			ax4.plot(a4xlim,[splist1[i],splist1[i]],'k:')
	py.setp(ax3.get_xticklabels(),rotation=45)#,visible=False)
	py.setp(ax3.get_yticklabels(),visible=False)
	py.setp(ax4.get_xticklabels(),visible=False)

	ax3.set_ylim(splist1[0],splist2[-1])
	ax4.set_ylim(splist1[0],splist2[-1])

	ax3.set_xlim(*a3xlim)
	ax4.set_xlim(a4xlim[0]*1.05,a4xlim[1]*0.95)
	ax4.set_ylabel('Orbital phase')
	ax3.set_xlabel('EW\n(OVIII Ly$\\alpha$)')
	ax4.annotate('A', rotation=90, xy=(-2, splist1[3]),  xycoords='data',
                horizontalalignment='center', verticalalignment='center')
	ax4.annotate('B', rotation=90, xy=(-2, splist1[6]),  xycoords='data',
                horizontalalignment='center', verticalalignment='center')
	ax4.annotate('C', rotation=90, xy=(-2, splist1[16]),  xycoords='data',
                horizontalalignment='center', verticalalignment='center')
	ax4.annotate('D', rotation=90, xy=(-2, splist1[19]),  xycoords='data',
                horizontalalignment='center', verticalalignment='center')

	ax.annotate('Wavelenght ($\\AA$)', rotation=0, xy=(0.5, 0.025),  xycoords='axes fraction',
                horizontalalignment='center', verticalalignment='center')


	ax3.set_xticks([-1,-3,-5])
	
	ax11.set_xticks([24.4,24.8,25.2])
	ax21.set_xticks([24.4,24.8,25.2])

	ax12.set_xticks([18.8,19,19.2])
	ax22.set_xticks([18.8,19,19.2])

	ax13.set_xticks([14,15,16,17])
	ax23.set_xticks([14,15,16,17])

	if opt.savefig:
		print 'Saving figure...'
		py.savefig('/Users/tiago/Dropbox/Documents/paper_cal87/Figures/trailedspec.eps')
	py.show()


######################################################################

if __name__ == '__main__':

	main(sys.argv)