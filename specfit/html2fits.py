#!/usr/bin/env python

'''
	Convert html tables from http://www.sdss-wdms.org/ to fits tables.
'''

import sys,os
import numpy as np
import pyfits
from xml.etree import ElementTree as ET
import logging as log

################################################################################

def main(argv):
	
	log.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
					level=log.INFO)

	from optparse import OptionParser

	parser = OptionParser()

	parser.add_option('-f','--filename',
					help = 'Input spectrum to fit.'
					,type='string')

	opt,args = parser.parse_args(argv)

	fp = open(opt.filename,'r')

	s = fp.readline()

	table = ET.XML(s)
	rows = iter(table)
	headers = [col.text for col in next(rows)]

	colFormats = ['D','24A','10A','D','D','D','D','E','E','E','E','E','E','E',
				  'E','E','E','D','E','E','E','E','E','E','E','E','E','E','E',
				  'E','E','E','D','D']
				  

	data = []

	for row in rows:
		data.append([str(col.text).replace('None','-99') for col in row])

	data=np.array(data,dtype='S').T

	colData = []

	for ncol in range(len(data)):
		colData.append(pyfits.Column(name=headers[ncol],
									 format=colFormats[ncol],
									 array=data[ncol]))

	cols = pyfits.ColDefs(colData)

	tbhdu = pyfits.BinTableHDU.from_columns(cols)

	prihdu = pyfits.PrimaryHDU(n)

	thdulist = pyfits.HDUList([prihdu, tbhdu])

	hdulist.writeto(opt.filename.replace('.html','.fits'))

################################################################################

if __name__ == '__main__':

	main(sys.argv)

################################################################################