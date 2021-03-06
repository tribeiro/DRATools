#! /usr/bin/env python

import os, sys
import numpy as np
import pylab as py
import logging as log
# import pymc
from astropy.table import Table


################################################################################

def main(argv):
    log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
                    level=log.INFO)

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-f', '--filename',
                      help='Input spectrum to fit.'
                      , type='string')
    parser.add_option('-o', '--output',
                      help='Input spectrum to fit.'
                      , type='string')

    opt, args = parser.parse_args(argv)

    csvlist = np.loadtxt(opt.filename, dtype='S', unpack=True, ndmin=2)

    if not opt.output:
        root = 'out_' + opt.filename
        ldot = root.rfind('.')
        if ldot > 0:
            root = root[:ldot] + '.npy'
        else:
            root += '.npy'
        opt.output = root

    fsize = np.max(np.array([len(ff) for ff in csvlist[0]]))

    dtype = [('s1', '<f8'), ('v1', '<f8'),
             ('s2', '<f8'), ('v2', '<f8'),
             ('t1_0', '<i4'), ('t1_1', '<i4'),
             ('t2_0', '<i4'), ('t2_1', '<i4'), ('t2_2', '<i4'),
             ('chi2', '<f8'), ('fname', 'S%i' % fsize)]

    mcres = np.zeros(len(csvlist[0]), dtype=dtype)

    for i, l in enumerate(csvlist[0]):

        log.info('Reading in %s...' % (l))
        try:
            data = Table.read(l, format='ascii')

            mcres['s1'][i] = data['Mean'][np.where(data['Parameter'] == 'scale1')[0][0]]
            mcres['v1'][i] = data['Mean'][np.where(data['Parameter'] == 'velocity1')[0][0]]
            mcres['s2'][i] = data['Mean'][np.where(data['Parameter'] == 'scale2')[0][0]]
            mcres['v2'][i] = data['Mean'][np.where(data['Parameter'] == 'velocity2')[0][0]]
            mcres['t1_0'][i] = data['Mean'][np.where(data['Parameter'] == 'template_01')[0][0]]
            mcres['t1_1'][i] = data['Mean'][np.where(data['Parameter'] == 'template_02')[0][0]]
            mcres['t2_0'][i] = data['Mean'][np.where(data['Parameter'] == 'template_03')[0][0]]
            mcres['t2_1'][i] = data['Mean'][np.where(data['Parameter'] == 'template_04')[0][0]]
            # mcres['t2_2'][i] = data['Mean'][8]

            mcres['fname'][i] = l
            sp = np.load(l.replace('.csv', '.spres.npy'))
            mcres['chi2'][i] = np.mean((sp['data'] - sp['model']) ** 2. / sp['model'])

            # try:
            # except:
            #     mcres['chi2'][i] = -1.

        except:
            log.exception(sys.exc_info())
            pass

    log.info('Saving output result to %s' % opt.output)
    np.save(opt.output, mcres)
    return 0


################################################################################


if __name__ == "__main__":
    main(sys.argv)

    ################################################################################
