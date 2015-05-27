#! /usr/bin/env python

__author__ = 'tiago'

import sys, os
import logging as log
import pylab as py
import numpy as np
from astropy.table import Table
# from astropy.io import fits as pyfits

################################################################################

def main(argv):
    '''
    Read fits file generated from stilts with cross match information and
    generate catalog with light curves
    '''

    log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=log.DEBUG)

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-f', '--filename',
                      help='FITS binary table.'
                      , type='string')

    parser.add_option('-t', '--time',
                      help='File with the time of the observations.'
                      , type='string')

    parser.add_option('-o', '--output',
                      help='Output file name root (0000.txt will be added, where 0000 is the source id.).'
                      , type='string')

    opt, args = parser.parse_args(argv)


    log.info('Reading in input catalog: %s '%opt.filename)

    mcat = Table.read(opt.filename,format='fits')

    log.info('Reading in time table: %s'%opt.time)

    time = Table.read(opt.time,format='ascii.commented_header')

    MAG = 'MAG_BEST_%i'
    MAGERR = 'MAGERR_BEST_%i'
    FLUX = 'FLUX_AUTO_%i'
    FLUXERR = 'FLUXERR_AUTO_%i'

    dtype = [('MJD' , np.float),
             ('MAG' , np.float),
             ('MAGERR' , np.float) ]
             # ('FLUX' , np.float),
             # ('FLUXERR' , np.float)]

    # for i in range(len(time)):
    #     dtype.append((MAG%(i+1),
    #                   np.float))
    #     dtype.append((MAGERR%(i+1),
    #                   np.float))

    lccat = np.zeros(len(time),dtype=dtype)

    for istar in range(len(mcat)):

        if istar % 100 == 0:
            log.debug('Working %i/%i ...'%(istar,len(mcat)))

        for itime in range(len(time)):
            lccat['MJD'][itime] = time['MJD'][itime]
            lccat['MAG'][itime] = mcat[MAG%(itime+1)][istar]
            lccat['MAGERR'][itime] = mcat[MAGERR%(itime+1)][istar]
            # lccat['FLUX'][itime] = mcat[FLUX%(itime+1)][istar]
            # lccat['FLUXERR'][itime] = mcat[FLUXERR%(itime+1)][istar]

        np.savetxt(opt.output+'_%04i.txt'%istar,fmt='%15.7f %10.6f %9.5f',X=lccat,header='MJD MAG MAGERR')

    return 0

################################################################################

if __name__ == '__main__':

    main(sys.argv)

################################################################################