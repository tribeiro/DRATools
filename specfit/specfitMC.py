
'''
Setup model for pymc fit.

C - Tiago Ribeiro
'''

import sys,os
import numpy as np
import pylab as py
import specfitF as spf
import pymc
from pymc import MCMC
import logging

################################################################################

def ModelFactory(ncomp,ofile,templist):
	'''
A factory of model to do the spectroscopic fit with PyMC.

Input:
		ncomp		- The number of spectroscopic components to fit.
		ofile		- The observed spectra.
		templist	- The template list.
C - Tiago Ribeiro
	'''

	spMod = spf.SpecFit(ncomp)

	# Load observed spectra as Pickle file
	
	if ofile.rfind('.fits') > 0:
		spMod.loadSDSSFits(ofile,True)
	elif ofile.rfind('.npy') > 0:
		spMod.loadPickle(ofile)
	else:
		raise IOError('Cannot read %s data type. Only fits and numpy (pickle) \
                      files are suported.'%(ofile))
	
	# Load template spectra, for each component as Picke files

	spMod.grid_ndim[0] = 2
	for i in range(ncomp):
		spMod.loadPickleTemplate(i,templist[i])

	# Pre-process template files

	spMod.normTemplate(0,5500.,5520.)
	spMod.preprocTemplate()

	# Prepare PyMC stochastic variables

	maxlevel,minlevel = spMod.suitableScale()
	level = maxlevel
	maxlevel *= 2.0
	minlevel /= 2.0

	min = np.zeros(ncomp)+minlevel
	val = np.zeros(ncomp)+level
	max = np.zeros(ncomp)+maxlevel

	scales = pymc.Uniform('scale', min, max, value=val,size=ncomp)
	min,val,max = np.zeros(ncomp)-300.,np.zeros(ncomp),np.zeros(ncomp)+300.
	velocity = pymc.Uniform('velocity', min, max , value=val,size=ncomp)

	gridmin = np.zeros(ncomp*np.sum(spMod.grid_ndim),dtype=int)
	gridmax = np.zeros(ncomp*np.sum(spMod.grid_ndim),dtype=int)
	for i in range(ncomp):
		gridmax[i*2] = len(spMod.Grid[0])-1
		gridmax[i*2+1] = len(spMod.Grid[0][i])-1

	#max = np.array([len(spMod.template[i])-1 for i in range(ncomp)],dtype=int)
	val = gridmax/2
		
	template = pymc.DiscreteUniform('template', lower=gridmin, upper=gridmax,
                                    value=val,
									size=ncomp*np.sum(spMod.grid_ndim))
	# Prepare PyMC deterministic variables
	
	@pymc.deterministic
	def spModel(scales=scales,velocity=velocity,template=template):
		for i in range(len(scales)):
			logging.debug('spModel: %i %e %f %i %i'%(i,scales[i],velocity[i],
                                                     template[i],template[i+1]))
			spMod.scale[i] = scales[i]
			spMod.vel[i] = velocity[i]
			spMod.ntemp[i] = spMod.Grid[i][template[i]][template[i+1]]
		modspec = spMod.modelSpec()
		return modspec.flux

	mflux = np.mean(spMod.ospec.flux)
	sig = pymc.Uniform('sig', mflux/100., mflux/10., value=mflux/50.)
	y = pymc.Normal('y', mu=spModel, tau=1.0/sig**2, value=spMod.ospec.flux,
                    observed=True)

	return locals()

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
    parser.add_option('-g','--grid',
                      help = 'List of grid spectra.'
                      ,type='string')
    parser.add_option('-v','--verbose',
                      help = 'Run in verbose mode.',action='store_true',
                      default=False)
    parser.add_option('--savefig',
                      help = 'Save png with output.',action='store_true',
                      default=False)
    parser.add_option('--show',
                      help = 'Show figure with output.',action='store_true',
                      default=False)
    opt,args = parser.parse_args(argv)

    dfile = opt.filename
    outfile = opt.output
    tlist = opt.grid

    M = pymc.MCMC(	ModelFactory( 1, dfile,
                                    [tlist] ) ,
                    db = 'pickle')


    '''
    py.plot(M.spMod.ospec.x,M.spMod.ospec.flux,'r')
    for i in range(len(M.spMod.template[0])):
        M.spMod.ntemp[0] = i
    #print M.spMod.Grid

        mspec = M.spMod.modelSpec()
        py.plot(mspec.x,mspec.flux,'b')


    py.show()

    '''

    M.sample(iter=10000, burn=1000,thin=5,verbose=-1)
#,tune_interval=1000,tune_throughout=True,verbose=0)

    grid = np.array(M.trace('template')[:]).reshape(2,-1)

    oarray = np.zeros(	len(M.trace('scale')[:]),
                        dtype=[('scale', '<f8'), ('velocity', '<f8'),
                               ('temp1', '<i4') , ('temp2', '<i4')])


    oarray['scale'] = np.array(	[i[0] for i in M.trace('scale')[:]] )
    oarray['velocity'] = np.array(	[i[0] for i in M.trace('velocity')[:]] )
    oarray['temp1'] = np.array(	[i[0] for i in M.trace('template')[:]] )
    oarray['temp2'] = np.array(	[i[1] for i in M.trace('template')[:]] )

    np.save(outfile,oarray)

    py.subplot(241)
    hh,edges = np.histogram(oarray['scale'],range=[M.minlevel,M.maxlevel*1.2])
    width = np.mean(edges[1:]-edges[:-1])/2.
    py.bar(edges[:-1],hh+1e-3,width=width)

    py.subplot(242)
    py.hist(oarray['velocity'])

    py.subplot(243)

    hh,edges = np.histogram(oarray['temp1'],bins=np.arange(-0.5,M.gridmax[0]))
    py.bar(edges[:-1]+0.1,hh+1e-3)

    py.subplot(244)
    hh,edges = np.histogram(oarray['temp2'],bins=np.arange(-0.5,M.gridmax[1]))
    py.bar(edges[:-1]+0.1,hh+1e-3)

    py.subplot(212)
    mspec = M.spMod.modelSpec()
    py.plot(M.spMod.ospec.x,M.spMod.ospec.flux)
    py.plot(mspec.x,mspec.flux)

    if opt.savefig:
        logging.info('Saving figure to %s'%(opt.output+'.png'))
        py.savefig(opt.output+'.png')
    if opt.show:
        py.show()

    logging.info('Done')


################################################################################

if __name__ == '__main__':

    main(sys.argv)

################################################################################
