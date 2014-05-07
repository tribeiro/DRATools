
import numpy as np
from scipy.optimize import leastsq
import pylab as py


################################################################################

func = lambda p,x: p[0] * np.exp(-((x-p[1])/p[2])**2.)
errfunc = lambda p,x,y: y - func(p,x)

################################################################################

def piecewise_dft(npieces,t,y,f):

	power = np.zeros(npieces*len(f)).reshape(npieces,-1)

	sz = len(t)/npieces
	
	for nn in range(npieces):
		power[nn] = dft(t[sz*nn:sz*(nn+1)],y[sz*nn:sz*(nn+1)],f)

	return power

################################################################################

def dft(t,y,f):
	"""
	It's written to be as fast as possible.
	I've used numpy ufuncs. If you don't use them, this function becomes
	EXTREMELY slow!
	Maybe I'll have to write it in C later but I'm satisfied now.
	"""
	
	#  t  = numpy.delete( gv.t, gv.delete ) # gv.t without deleted points
	nt = float(len(t))
	nf=len(f)

	dft = np.zeros(nf, dtype=float) # Allocate memory
	w = 2*np.pi*np.array(f)                  # Angular frequencies
  
	# Transform y values subtracted from mean
	#dy = []
	#for i in range(0,ny):
	#y = np.delete( Cy[i], delete ) # Cy without the deleted points
	mean = np.mean( y )          # Scalar
	dy = y-mean             # list of lists dim: [ny,nt]

	for k in range(0,nf):
		C2 = np.cos( w[k]*t )           # Array with nt positions
		S2 = np.sin( w[k]*t )           # Array with nt positions
		#for i in range(0,ny):
		sum1  = np.inner(dy,C2)    # Inner vector product between dy and C2
		sum2  = np.inner(dy,S2)    # Inner vector product between dy and C2
		dft[k] = 2.0*np.hypot(sum1,sum2)/nt # Scalar
	return dft

################################################################################

def findPeriod(xx,yy):
	'''
	Fit gaussian.
	'''

	A0 = (yy.max(),xx[yy.argmax()],np.std(xx))
	A1,success = leastsq(errfunc,A0,args=(xx,yy))

	return A1

################################################################################
