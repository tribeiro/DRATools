#! /usr/bin/env python

import sys,os
import numpy as np
import logging

################################################################################

def readGrid(arr):

    T,logg = np.array([os.path.basename(ff)[2:].replace('.npy','').split('_') for ff in arr[0]]).T

    Tgrid = np.array(np.unique(T),dtype=float)
    logg_grid = np.array(np.unique(logg),dtype=float)

    return Tgrid,logg_grid

################################################################################

def main(argv):
    '''Take the results of spefitMC.py and the grid-list used during the fitting
procedure and save the result to a file.
'''

    logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
    level=logging.INFO)

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-f','--filename',
    help = 'Input list of spefitMC results.'
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
    opt,args = parser.parse_args(argv)

    mcres = np.loadtxt(opt.filename,dtype='S',ndmin=1)

    grid = np.loadtxt(opt.grid,dtype='S',ndmin=1,unpack=True)

    maxlen = np.max(np.array([len(fname) for fname in mcres]))
    
    odat = np.zeros(	len(mcres),
                        dtype=[('mscale', '<f8'), ('escale', '<f8'),
                               ('mrv', '<f8'), ('erv', '<f8'),
                               ('T', '<f8') , ('eT', '<f8') ,
                               ('logg', '<f8'), ('elogg', '<f8'),
                               ('fname','|S%i'%maxlen)])

    Tgrid,logg_grid = readGrid(grid)
    
    logging.info('Running...')
    
    for i in range(len(mcres)):
        logging.info('Working on %s'%mcres[i])
        mc = np.load(mcres[i])
        
        odat['mscale'][i] = np.mean(mc['scale'])
        odat['escale'][i] = np.std(mc['scale'])
        odat['mrv'][i] = np.mean(mc['velocity'])
        odat['erv'][i] = np.std(mc['velocity'])
        odat['T'][i] = np.mean(Tgrid[mc['temp1']])
        odat['eT'][i] = np.std(Tgrid[mc['temp1']])
        odat['logg'][i] = np.mean(logg_grid[mc['temp2']])
        odat['elogg'][i] = np.std(logg_grid[mc['temp2']])
        odat['fname'][i] = mcres[i]
    
    logging.info('Saving output to %s'%(opt.output))
    np.save(opt.output,odat)

################################################################################

if __name__ ==  '__main__':

    main(sys.argv)

################################################################################
