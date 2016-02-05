#! /usr/bin/env python

import sys, os
import numpy as np
import pylab as py
from astropy.io import fits as pyfits


################################################################################

def main(argv):
    _file = '/Volumes/TiagoHD2/Documents/data/wdms.fits'

    hdu = pyfits.open(_file)

    # mask = np.bitwise_and(np.bitwise_and(hdu[1].data['M2'] > 0,
    #                                      hdu[1].data['dwd'] > 0),
    #                       hdu[1].data['M2e'] > 0 )

    mask = np.bitwise_and(hdu[1].data['M2'] > 0,
                          hdu[1].data['dwd'] > 0)


    mask[mask] = hdu[1].data['dwde'][mask] / hdu[1].data['dwd'][mask] < 0.15

    py.plot(hdu[1].data['M2'][mask],
            (hdu[1].data['dsec'][mask] - hdu[1].data['dwd'][mask]) / hdu[1].data['dwd'][mask], '.')

    # py.hist(hdu[1].data['M2e'][mask]/hdu[1].data['M2'][mask])

    py.show()


################################################################################

if __name__ == '__main__':
    main(sys.argv)

    ################################################################################
