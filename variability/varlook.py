#!/usr/bin/env python
##!/usr/bin/env python2.6
# Author				version		Up-date			Description
#------------------------------------------------------------------------
# T. Ribeiro (SOAR)		0.0			09 Jun 2011     Creation

'''
	
varlook.py - GUI for looking up variability.

	Ribeiro, T., June 2011.
	
'''

from vartool import *

if __name__ == "__main__":
	
	logging.basicConfig(format='%(levelname)s:%(asctime)s::%(message)s',
						level=logging.DEBUG)

	
	root = QtGui.QApplication(sys.argv)
	
	usergui = VarAnDa()
	
	usergui.initGUI()
	
	usergui.show()
	
	sys.exit(root.exec_())
