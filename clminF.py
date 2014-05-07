#! /usr/bin/env python

'''
	Find minimum on light curve by fitting a gaussian, or a polynome.
	
	c - Tiago Ribeiro 16/12/2014
'''

import os,sys
import numpy as np
import pylab as py
import pyfits
import pymc

# read data

_path = os.path.expanduser('~/Google Drive/CAL87/emap_0305keV_rateall')
#_cldat = 'cal87_0305keV_rateall.dat.122' #'cal87_0305keV_rateall.dat.122'
_cldat = '../cal87_0153250101_b250s_0305keV_master_pnm1m2.tfits' #'cal87_0305keV_rateall.dat.122'

table = pyfits.open(os.path.join(_path,_cldat))
time_hjd = table[1].data['TIME']/86400.+2450814.5000
rate_all = table[1].data['RATE_ALL']
error_all = table[1].data['ERROR_ALL']

#priors
sig = pymc.Uniform('sig', 0.0, 100.0, value=1.)

root = pymc.Uniform('k', 50, 300, value= 150)

#model
@pymc.deterministic(plot=False)
def mod_sinusoid(k=k, g=g, df=df):
      return k*np.sin(2.*np.pi*(x+df))+g

#likelihood
y = pymc.Normal('y', mu=mod_sinusoid, tau=1.0/sig**2, value=f, observed=True)


