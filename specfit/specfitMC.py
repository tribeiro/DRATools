
'''
Setup model for pymc fit.

C - Tiago Ribeiro
'''

import sys,os
import numpy as np
import matplotlib.pyplot as py
from StringIO import StringIO
import specfitF as spf
import pymc
from pymc import MCMC
from pymc.Matplot import plot
import logging

################################################################################

def ModelFactory(ncomp,ofile,templist,temptype=1):
	'''
A factory of model to do the spectroscopic fit with PyMC.

Input:
		ncomp		- The number of spectroscopic components to fit.
		ofile		- The observed spectra.
		templist	- The template list.
        temptype    - Type of template spectra. (Chooses read algorithm
                      1 - Pickle
                      2 - SDSSFits
                      3 - Coelho 2014 model spectra
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
	
	for i in range(ncomp):
		fp = open(templist[i],'r')
		line1 = StringIO(fp.readline())
		line1 = np.loadtxt(line1,dtype='S')
		spMod.grid_ndim[i] = len(line1)-1 # Set grid dimension for 1st component

		logging.debug('Component %s[%i] with %i dimentions.'%(templist[i],i,spMod.grid_ndim[i]))

		if temptype == 1:
			spMod.loadPickleTemplate(i,templist[i])
		elif temptype == 2:
			spMod.loadSDSSFitsTemplate(i,templist[i])
		elif temptype == 3:
			spMod.loadCoelhoTemplate(i,templist[i])

	# Pre-process template files

	spMod.normTemplate(0,5500.,5520.)
	spMod.normTemplate(1,5500.,5520.)

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
	min,val,max = np.zeros(ncomp)-600.,np.zeros(ncomp),np.zeros(ncomp)+600.
	velocity = pymc.Uniform('velocity', min, max , val ,size=ncomp)

	gridmin = np.zeros(np.sum(spMod.grid_ndim),dtype=int)
	gridmax = np.zeros(np.sum(spMod.grid_ndim),dtype=int)
	
	for i in range(ncomp):
		logging.debug('gridmax: %i %i %i %i'%(i*2,i*2+1,
											  len(spMod.Grid[i])-1,
											  len(spMod.Grid[i][0])-1))
		for j in range(spMod.grid_ndim[i]):
			gridmax[i*2+j] = spMod.Grid[i].shape[j]-1
		#gridmax[i*2+1] = len(spMod.Grid[i][0])-1

	#max = np.array([len(spMod.template[i])-1 for i in range(ncomp)],dtype=int)
	val = gridmax/2

	template = pymc.DiscreteUniform('template', lower=gridmin, upper=gridmax,
                                    value=val,
									size=np.sum(spMod.grid_ndim))
	# Prepare PyMC deterministic variables
	
	@pymc.deterministic
	def spModel(scales=scales,velocity=velocity,template=template):
		#logging.debug('spModel: len(spMod.Grid) = %i'%(len(spMod.Grid)))
		#logging.debug('spModel: Ncomp   Scale   Vel temp1 temp2 lenGrid[0] lenGrid[1]')
		strlog = "spModel: "

		for idx in range(len(scales)):
		
			strlog += '%5i %6.4f %5.1f '%(idx,scales[idx],
										  velocity[idx])
			
			spMod.scale[idx] = scales[idx]
			spMod.vel[idx] = velocity[idx]
			index = np.zeros(spMod.grid_ndim[idx],dtype=int)
			for iidx in range(spMod.grid_ndim[idx]):
				strlog += '%5i '%template[idx*2+iidx]
				index[iidx] = template[idx*2+iidx]
			spMod.ntemp[idx] = spMod.Grid[idx].item(*index)
			
		logging.debug(strlog)
		#	strlog = "spModel: "
			
		modspec = spMod.modelSpec()
		return modspec.flux

	mflux = np.mean(spMod.ospec.flux)
	#sig = pymc.Uniform('sig',
	#				   np.median(spMod.ospec.err),
	#				   np.median(spMod.ospec.flux),
	#				   value=np.median(spMod.ospec.flux)/2.)
	sig = np.zeros_like(spMod.ospec.err)+np.median(spMod.ospec.flux)/2.
	#mask = spMod.ospec.x < 5000.
	#err[mask] = spMod.ospec.err[mask]/10.
	y = pymc.Normal('y', mu=spModel,
					tau=1./sig**2.,
					value=spMod.ospec.flux,
                    observed=True)

	return locals()

################################################################################


def main(argv):

    logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                        level=logging.DEBUG)

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
    parser.add_option('-t','--template-list',
                      help = '''List of list of grid spectra. Use when the 
number of components to fit is larger than 1.'''
                      ,type='string')
    parser.add_option('--n-comp',
					help = '''The number of components to fit. By default only 
one is used.''',type='int',default=1)
    parser.add_option('--niter',
					  help = "Number of iterations (default=10000).",
					  type='int',default=10000)
    parser.add_option('--burn',
					  help = "Number of burn iterations (default=2500).",
					  type='int',default=2500)
    parser.add_option('--thin',
					  help = "Number of sub-iterations for each iteration (default=3).",
					  type='int',default=3)
    parser.add_option('--tune_interval',
					  help = "Number of iterations for tuning (default=500).",
					  type='int',default=500)
    parser.add_option('--tune_throughout',
                      help = 'Run in verbose mode (default = False).',action='store_true',
					  default=False)
    parser.add_option('--templatetype',
					help = '''Type of template file. Choices are: 1 - Pickle,
2 - SDSSFits, 3 - Coelho 2014 model spectra''',type='int',default=1)
    parser.add_option('--no-overwrite',
                      help = 'Check if output file exists before writing to it. Save to a different file if it exists.',
					  action='store_true',
                      default=False)
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

    threadId = os.getpid()
	
    dfile = opt.filename
    outfile = opt.output
    outroot = opt.output[:opt.output.rfind('.')]
    tlist = [opt.grid]

    outfile = outroot+'_%i.npy'%threadId
    dbname = outroot+'_%i.pickle'%threadId
    spname = outroot+'_%i.spres.npy'%threadId
    if opt.no_overwrite and os.path.exists(dbname):
        logging.debug('File %s exists (running on "no overwrite" mode).'%dbname)
        index = 0
        dbname = outroot + '_%i.%04i.pickle'%(threadId,index)
        while os.path.exists(dbname):
            dbname = outroot + '_%i.%04i.pickle'%(threadId,index)
            index+=1
            logging.debug('%s'%dbname)
	fp = open(dbname,'w')
	fp.close()
	
	logging.info('dbname: %s'%dbname)
    if opt.no_overwrite and os.path.exists(spname):
        logging.debug('File %s exists (running on "no overwrite" mode).'%spname)
        index = 0
        spname = outroot + '_%i.spres.%04i.npy'%(threadId,index)
        while os.path.exists(spname):
            spname = outroot + '_%i.spres.%04i.npy'%(threadId,index)
            index+=1
            logging.debug('%s'%spname)
	fp = open(spname,'w')
	fp.close()

	logging.info('spname: %s'%spname)

    if opt.no_overwrite and os.path.exists(outfile):
        logging.debug('File %s exists (running on "no overwrite" mode).'%outfile)
        index = 0
        outroot = outfile[:opt.filename.rfind('.')]
        outfile = outroot + '_%i.%04i.npy'%(threadId,index)
        while os.path.exists(outfile):
            outfile = outroot + '_%i.%04i.npy'%(threadId,index)
            index+=1
            logging.debug('%s'%outfile)

	fp = open(outfile,'w')
	fp.close()

    logging.info('outfile: %s'%outfile)

    csvname=outroot+'_%i.csv'%(threadId)
    if opt.no_overwrite and os.path.exists(csvname):
        logging.debug('File %s exists (running on "no overwrite" mode).'%csvname)
        index = 0
        csvname = outroot + '_%i.%04i.csv'%(threadId,index)
        while os.path.exists(csvname):
            csvname = outroot + '_%i.%04i.csv'%(threadId,index)
            index+=1
            logging.debug('%s'%csvname)

	fp = open(csvname,'w')
	fp.close()

	logging.info('csvname: %s'%csvname)

    logging.info('Preparing model...')
	
    if opt.n_comp > 1:
		tlist = np.loadtxt(opt.template_list,dtype='S')
    elif not opt.grid:
		tlist = np.loadtxt(opt.template_list,dtype='S',ndim=1)

    M = pymc.MCMC(	ModelFactory( opt.n_comp, dfile,
                                     tlist, opt.templatetype) ,
                    db = 'pickle',
					dbname=dbname)

    M.use_step_method(pymc.DiscreteMetropolis, M.template,
					  proposal_distribution='Normal')
    #M.use_step_method(pymc.AdaptiveMetropolis,)
    logging.info('Model done...')

    '''
    temp1 = [9,9,8, 9, 8, 7, 8, 7]
    temp2 = [8,9,9,10,10,10,11,11]
	
    for i in range(len(temp1)):
        M.spMod.ntemp[0] = M.spMod.Grid[0][temp1[i]][temp2[i]]
        mspec = M.spMod.modelSpec()
        py.plot(mspec.x,mspec.flux,'-')

    py.show()
    return 0

    py.plot(M.spMod.ospec.x,M.spMod.ospec.flux,'r')
    for i in range(len(M.spMod.template[0])):
        M.spMod.ntemp[0] = i
    #print M.spMod.Grid

        mspec = M.spMod.modelSpec()
        py.plot(mspec.x,mspec.flux,'b')


    py.show()

    '''
	
    #print M.spMod.templateScale
    #return 0

    logging.info('Starting sampler...')
    #M.sample(iter=70000,burn=40000,thin=3,verbose=0)#,verbose=-1),thin=3
    M.sample(iter=opt.niter,burn=opt.burn,thin=opt.thin,
			tune_interval=opt.tune_interval,tune_throughout=opt.tune_throughout,
			verbose=-1)
#,tune_interval=1000,tune_throughout=True,verbose=0)

    logging.info('Sampler done. Saving results...')

    M.db.close()

    M.write_csv(csvname,variables=['scale','velocity','template'])
	
    #grid = np.array(M.trace('template')[:]).reshape(2,-1)

    oarray = np.zeros(	len(M.trace('scale')[:]),
                        dtype=[('scale1', '<f8'), ('vel1', '<f8'),
							   ('scale2', '<f8'), ('vel2', '<f8'),
							   ('tempscale1', '<f8'), ('tempscale2', '<f8'),
                               ('temp1_1', '<i4') , ('temp1_2', '<i4'),
							   ('temp2_1', '<i4') , ('temp2_2', '<i4'),
							   ('temp2_3', '<i4') , ('sig', '<f8')])


    oarray['scale1'] = np.array(	[i[0] for i in M.trace('scale')[:]] )
    oarray['scale2'] = np.array(	[i[1] for i in M.trace('scale')[:]] )
    oarray['vel1'] = np.array(	[i[0] for i in M.trace('velocity')[:]] )
    oarray['vel2'] = np.array(	[i[1] for i in M.trace('velocity')[:]] )
    oarray['temp1_1'] = np.array(	[i[0] for i in M.trace('template')[:]] )
    oarray['temp1_2'] = np.array(	[i[1] for i in M.trace('template')[:]] )
    oarray['temp2_1'] = np.array(	[i[2] for i in M.trace('template')[:]] )
    oarray['temp2_2'] = np.array(	[i[3] for i in M.trace('template')[:]] )
    #oarray['temp2_3'] = np.array(	[i[4] for i in M.trace('template')[:]] )
    #oarray['sig'] = np.array(	[i for i in M.trace('sig')[:]] )
	
    for idx in range(2):
		for icomp in range(len(oarray['temp1_1'])):
			index = np.zeros(M.spMod.grid_ndim[idx],dtype=int)
			for iidx in range(M.spMod.grid_ndim[idx]):
				index[iidx] = oarray['temp%i_%i'%(idx+1,iidx+1)][icomp]
			ntemp = M.spMod.Grid[idx].item(*index)
			oarray['tempscale%i'%(idx+1)][icomp] = M.spMod.templateScale[idx][ntemp]


    np.save(outfile,oarray)

    mspec = M.spMod.modelSpec()
    scale1 = M.spMod.scale[0]

    M.spMod.scale[0] = 0.
    mspec1 = M.spMod.modelSpec()

    M.spMod.scale[0] = scale1
    M.spMod.scale[1] = 0.
    mspec2 = M.spMod.modelSpec()

    sp_array = np.zeros(	len(mspec.x),
				  dtype=[('wave', '<f8'), ('data', '<f8'), ('model', '<f8'),
						 ('model1', '<f8') , ('model2', '<f8')])

    sp_array['wave'] = mspec.x
    sp_array['data'] = M.spMod.ospec.flux
    sp_array['model'] = mspec.flux
    sp_array['model1'] = mspec1.flux
    sp_array['model2'] = mspec2.flux
	
    np.save(spname,sp_array)
	
    py.subplot(241)
    hh,edges = np.histogram(oarray['scale1'],range=[M.minlevel,M.maxlevel*1.2])
    width = np.mean(edges[1:]-edges[:-1])/2.
    py.bar(edges[:-1],hh+1e-3,width=width)

    hh,edges = np.histogram(oarray['scale2'],range=[M.minlevel,M.maxlevel*1.2])
    width = np.mean(edges[1:]-edges[:-1])/2.
    py.bar(edges[:-1],hh+1e-3,width=width)

    py.subplot(242)
    py.hist(oarray['vel1'])
    py.hist(oarray['vel2'])
	
    py.subplot(243)

    hh,edges = np.histogram(oarray['temp1_1'],bins=np.arange(-0.5,M.gridmax[0]))
    py.bar(edges[:-1]+0.1,hh+1e-3)

    py.subplot(244)
    hh,edges = np.histogram(oarray['temp1_2'],bins=np.arange(-0.5,M.gridmax[1]))
    py.bar(edges[:-1]+0.1,hh+1e-3)

    py.subplot(212)
	
    py.plot(M.spMod.ospec.x,M.spMod.ospec.flux,'0.8')
    py.plot(mspec.x,mspec.flux,'k')

    py.plot(mspec1.x,mspec1.flux,'r')
    py.plot(mspec2.x,mspec2.flux,'b')
	
    if opt.savefig:
        logging.info('Saving figure to %s'%(opt.output+'.png'))
        py.savefig(opt.output+'.png')
    if opt.show:
        plot(M)
        py.show()

    logging.info('Done')


################################################################################

if __name__ == '__main__':

    main(sys.argv)

################################################################################
