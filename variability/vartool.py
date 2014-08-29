
import sys,os

from PyQt4 import QtCore,QtGui,uic
import logging

from astropy.io import fits as pyfits
import numpy as np

from vtmodel import *

################################################################################
#
#

class VarAnDa(QtGui.QMainWindow):


	############################################################################
	#
	#
	
	def __init__(self):
		
		super(VarAnDa, self).__init__()
	
		self.uipath = os.path.join(os.path.dirname(__file__),
								   'gui/main.ui')

		self.obj_key = 'thingId'
		self.time_key = 'TAI_%s'
		self.mag_key = 'psfMag_%s'
		self.merr_key = 'psfMagerr_%s'

		self.band = 'ugriz'
		self.nband = len(self.band)

	#
	#
	############################################################################

	############################################################################
	#
	#

	def initGUI(self):

		self.ui = uic.loadUi(self.uipath,self)


		self.connect(self.ui.actionOpen, QtCore.SIGNAL('triggered()'),
					 self.OpenFits)
	
		model = VTModel()
		self.ui.treeView.setModel(model)

		self.connect(self.ui.treeView,
					 QtCore.SIGNAL("clicked(const QModelIndex&)"),
					 self.ItemSelected)

		self.ui.treeView.keyPressEvent = self.handleKeyEvent
		
		self.ui.spinBox.setMaximum(len(self.band)-1)
		self.ui.spinBox.setMinimum(0)
	
		self.connect(self.ui.spinBox,QtCore.SIGNAL("valueChanged(int )"),
					 self.filterChanged)

	#
	#
	############################################################################

	############################################################################
	#
	#
	
	def OpenFits(self):

		#fn = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
		#									   os.path.expanduser('~/Documents'))
		
		fn = '/Users/tiago/Documents/SDSSVar/MyTable_1_tribeiro.fit'
		logging.debug('Selected file %s'%(fn))

		self.hdu = pyfits.open(str(fn))

		self.processHDU()
	#
	#
	############################################################################

	############################################################################
	#
	#

	def processHDU(self):

		self.uobj = np.unique(self.hdu[1].data[self.obj_key])
		
		
		mask = np.bitwise_and(self.hdu[1].data[self.obj_key] == self.uobj[0],
							  self.hdu[1].data[self.mag_key%'g'] > 0)
		
		data = []
		for objn in self.uobj:
			for band in self.band:
				mask = np.bitwise_and(self.hdu[1].data[self.obj_key] == objn,
									  self.hdu[1].data[self.mag_key%band] > 0)
				
				input = [str(objn),band,len(mask[mask]),0]
				data.append(input)
		
		model = VTModel(data=data)
		self.ui.treeView.setModel(model)
		
		self.plot(0,0)
		self.processStat()

	#
	#
	############################################################################
	
	############################################################################
	#
	#
	
	def processStat(self):
		
		nband = len(self.band)
		
		mavg = np.zeros(len(self.uobj)*nband).reshape(nband,len(self.uobj))
		mstd = np.zeros(len(self.uobj)*nband).reshape(nband,len(self.uobj))
		eavg = np.zeros(len(self.uobj)*nband).reshape(nband,len(self.uobj))

		logging.debug('%i %i'%mavg.shape)

		for _nob in range(len(self.uobj)):
			for _nb in range(nband):
				logging.debug('%i %i'%(_nob,_nb))
				
				mask = np.bitwise_and(	self.hdu[1].data[self.obj_key] == self.uobj[_nob],
										self.hdu[1].data[self.mag_key%self.band[_nb]] > 0 )
				mavg[_nb][_nob] = np.mean(self.hdu[1].data[self.mag_key%self.band[_nb]][mask])
				mstd[_nb][_nob] = np.std(self.hdu[1].data[self.mag_key%self.band[_nb]][mask])
				eavg[_nb][_nob] = np.mean(self.hdu[1].data[self.merr_key%self.band[_nb]][mask])

		self.mavg = mavg
		self.mstd = mstd
		self.eavg = eavg
		
		self.plotStat(self.ui.spinBox.value())
	#
	#
	############################################################################
	
	############################################################################
	#
	#

	def ItemSelected(self,index):
		
		if index.parent().row() < 0:
			ix,iy = index.row(),self.ui.spinBox.value()
		else:
			ix,iy = index.parent().row(),index.row()
			self.ui.spinBox.setValue(iy)
		
		self.plot(ix,iy)
		self.plotStat(self.ui.spinBox.value())

	#
	#
	############################################################################

	############################################################################
	#
	#

	def selChanged(self,index1,index2):

		print 'changed'
	#
	#
	############################################################################

	############################################################################
	#
	#

	def filterChanged(self,iy):
		
		index = self.ui.treeView.currentIndex()
	
		if index.parent().row() == -1 and index.row() == -1:
			self.plot(0,iy)
		elif index.parent().row() == -1:
			self.plot(index.row(),iy)
		else:
			self.plot(index.parent().row(),iy)

		self.plotStat(iy)
	
	#
	#
	############################################################################
	
	############################################################################
	#
	#

	def plot(self,ix,iy):
		
		mask = np.bitwise_and(self.hdu[1].data[self.obj_key] == self.uobj[ix],
							  self.hdu[1].data[self.mag_key%self.band[iy]] > 0)

		self.ui.tab.axes.errorbar(	self.hdu[1].data[self.time_key%self.band[iy]][mask]/(24*3600),
								  self.hdu[1].data[self.mag_key%self.band[iy]][mask],
								  self.hdu[1].data[self.merr_key%self.band[iy]][mask],
								  fmt='o')
		avg = np.mean(self.hdu[1].data[self.mag_key%self.band[iy]][mask])
		std = np.std(self.hdu[1].data[self.mag_key%self.band[iy]][mask])
		eavg = np.mean(self.hdu[1].data[self.merr_key%self.band[iy]][mask])
		
		xlim = self.ui.tab.axes.get_xlim()
		self.ui.tab.axes.hold(True)
		
		self.ui.tab.axes.plot(xlim,[avg+eavg,avg+eavg],'r--')
		self.ui.tab.axes.plot(xlim,[avg,avg],'r-')
		self.ui.tab.axes.plot(xlim,[avg-eavg,avg-eavg],'r--')

		self.ui.tab.draw()
		self.ui.tab.axes.hold(False)

	#
	#
	############################################################################

	############################################################################
	#
	#

	def plotStat(self,iy):
		
		self.ui.tab_4.axes.plot(self.mavg[iy],
								self.mstd[iy],'o')
										
		self.ui.tab_4.draw()
	#
	#
	############################################################################
	
	############################################################################
	#
	#

	def handleKeyEvent(self,event):
		
		oldevent = QtGui.QTableWidget.keyPressEvent(self.ui.treeView, event)

		ix,iy = self.ui.treeView.selectedIndexes()[0].parent().row(),\
				self.ui.treeView.selectedIndexes()[0].row()
				
		
		if ix == -1 and iy == -1:
			self.plot(0,self.ui.spinBox.value())
		elif ix == -1:
			self.plot(iy,self.ui.spinBox.value())
		else:
			self.plot(ix,iy)

		return oldevent

	#
	#
	############################################################################

#
#
################################################################################

