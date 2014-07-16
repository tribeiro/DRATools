#! /usr/bin/env python

import sys,os
import numpy as np
from astropy.io import fits as pyfits
import logging

################################################################################

def main(argv):
    '''
        Get result of mcmatchgrid, a list that translate specfitMC result to 
        plate,mjd,fiberid and a fits file with plate,mjd,fiberid,Teff,logg and
        stores the matching results.
'''
    logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                        level=logging.INFO)

    from optparse import OptionParser
    
    parser = OptionParser()
    
    parser.add_option('-m','--mcmatchgrid',
                        help = 'Input list with mcmatchgrid result.'
                        ,type='string')
    parser.add_option('-t','--translate',
                      help = 'List that translate specfitMC result to sdss \
                      plate,mjd,fiberid.'
                      ,type='string')
    parser.add_option('-d','--database',
                      help = 'Fits file with Teff logg info.'
                      ,type='string')
    parser.add_option('-o','--output',
                        help = 'Output root name.'
                        ,type='string')
    parser.add_option('-v','--verbose',
                        help = 'Run in verbose mode.',action='store_true',
                        default=False)
    opt,args = parser.parse_args(argv)

    #Read mcmatchgrid file
    mcmgrid = np.load(opt.mcmatchgrid)
    
    # Read translate file
    translate = np.loadtxt(opt.translate,unpack=True,dtype='S')
    
    # Read database file
    hdu = pyfits.open(opt.database)
    aran1 = np.arange(len(translate[0]))
    aran2 = np.arange(len(hdu[1].data))
    odat = np.zeros(	len(mcmgrid),
                    dtype=[('Teff1', '<f8'), ('eTeff1', '<f8'),
                           ('logg1', '<f8'), ('elogg1', '<f8'),
                           ('Teff2', '<f8'), ('eTeff2', '<f8'),
                           ('logg2', '<f8'), ('elogg2', '<f8')])
    
    for i in range(len(mcmgrid)):

        logging.debug('Working in %s'%(mcmgrid['fname'][i]))
        
        idx_pmf = aran1[translate[0] == mcmgrid['fname'][i]][0]
        mask_plate = hdu[1].data['Plate'] == int(translate[1][idx_pmf])
        mask_mjd = hdu[1].data['MJD'] == int(translate[2][idx_pmf])
        mask_fiber = hdu[1].data['Fiber'] == int(translate[3][idx_pmf])
        mask = np.bitwise_and(mask_plate,np.bitwise_and(mask_mjd,mask_fiber))
        if mask.any():
            idx = aran2[mask][0]
            odat['Teff1'][i] =   hdu[1].data['Teff'][idx]
            odat['eTeff1'][i] =   hdu[1].data['e_Teff'][idx]
            odat['logg1'][i] =   hdu[1].data['log_g_'][idx]
            odat['elogg1'][i] =   hdu[1].data['e_log_g_'][idx]

            odat['Teff2'][i] = mcmgrid['T'][i]
            odat['eTeff2'][i] = mcmgrid['eT'][i]
            odat['logg2'][i] = mcmgrid['logg'][i]
            odat['elogg2'][i] = mcmgrid['elogg'][i]
        else:
            logging.warning('Could not find %s in list. Skiping...'%(mcmgrid['fname'][i]))
    np.save(opt.output,odat)
                           
    return 0
################################################################################

if __name__ == '__main__':

    main(sys.argv)

################################################################################
