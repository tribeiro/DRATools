
from StringIO import StringIO
import numpy as np

######################################################################

def read_mem(name):
	'''
	Read prida mem image. Ignore lines with information at the 
	bottom.
	'''

	# Get size of image from filename
	imgsize = int(name[name.rfind('.')+1:])
	
	fp = open(name,'r')
	data = fp.readlines()

	_fcontent = StringIO()

	for i in range(imgsize):
		_fcontent.write(data[i])
	_fcontent.flush()
	_fcontent.seek(0)
	return np.loadtxt(_fcontent,unpack=True)

######################################################################