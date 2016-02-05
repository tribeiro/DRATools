#! /usr/bin/env python

__author__ = 'tiago'

import sys,os
import numpy as np
import pylab as py

################################################################################

def main(argv):

    from optparse import OptionParser

    parser = OptionParser()

    opt,args = parser.parse_args(argv)

    fig1 = py.figure(1)
    ax1 = fig1.add_subplot(211)
    ax2 = fig1.add_subplot(212)

    fig2 = py.figure(2)
    ax3 = fig2.add_subplot(311)
    ax4 = fig2.add_subplot(312)
    ax5 = fig2.add_subplot(325)
    ax6 = fig2.add_subplot(326)

    # fig3 = py.figure(3)
    # ax6 = fig3.add_subplot(111)

    for f in args[1:]:
        print '->',f
        try:
            rr = np.loadtxt(f,unpack=True) #,usecols=(2,3,6,7))
            #if len(rr) > 4:
            ax1.plot(rr[0])
            ax2.plot(rr[1])
            # ax6.hist2d(rr[0],rr[1],bins=[np.arange(0,np.max(rr[0])),np.arange(0,np.max(rr[1]))])
            ax3.plot(rr[2])
            ax4.plot(rr[3])
            ax5.plot(rr[3],rr[1],'.')
            ax6.plot(rr[4],rr[1],'.')
        except:
            pass
    print 'Done'
    py.show()

    return 0

################################################################################

if __name__ == '__main__':

    main(sys.argv)

################################################################################