
from PyQt4 import QtGui, QtCore

HORIZONTAL_HEADERS = ("Filter", "Nobs")

################################################################################
#
#

class targetClass(object):
    '''
    a trivial custom data object
    '''
	
	############################################################################
	#
	#
    def __init__(self, objname, filter, nobs, isVar):
        self.objname = objname
        self.filter = filter
        self.nobs = nobs
        self.isVar = isVar

	#
	#
	############################################################################

	############################################################################
	#
	#
	
    def __repr__(self):
        return "PERSON - %s %s"% (self.fname, self.sname)

	#
	#
	############################################################################
#
#
################################################################################

################################################################################
#
#

class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''
	
	############################################################################
	#
	#
    def __init__(self, target, header, parentItem):
        self.target = target
        self.parentItem = parentItem
        self.header = header
        self.childItems = []
	
	#
	#
	############################################################################
	
	############################################################################
	#
	#
	
    def appendChild(self, item):
        self.childItems.append(item)

	#
	#
	############################################################################

	############################################################################
	#
	#

    def child(self, row):
        return self.childItems[row]

	#
	#
	############################################################################

	############################################################################
	#
	#

    def childCount(self):
        return len(self.childItems)

	#
	#
	############################################################################

	############################################################################
	#
	#

    def columnCount(self):
        return 2

	#
	#
	############################################################################

	############################################################################
	#
	#

    def data(self, column):
        if self.target == None:
            if column == 0:
                return QtCore.QVariant(self.header)
            if column == 1:
                return QtCore.QVariant("")                
        else:
            if column == 0:
                return QtCore.QVariant(self.target.filter)
            if column == 1:
                return QtCore.QVariant(self.target.nobs)
        return QtCore.QVariant()

	#
	#
	############################################################################

	############################################################################
	#
	#

    def parent(self):
        return self.parentItem

	#
	#
	############################################################################

	############################################################################
	#
	#

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

	#
	#
	############################################################################

#
#
################################################################################

################################################################################
#
#

class VTModel(QtCore.QAbstractItemModel):
    '''
		A mode to display Object name -> Filters
		'''

	############################################################################
	#
	#

    def __init__(self, parent=None,data=()):
		super(VTModel, self).__init__(parent)
		self.target = []
		for tname, fname, nobs, isvar in data:
			target = targetClass(tname, fname, nobs, isvar)
			self.target.append(target)
				
		self.rootItem = TreeItem(None, "ALL", None)
		self.parents = {0 : self.rootItem}
		self.setupModelData()

	#
	#
	############################################################################

	############################################################################
	#
	#

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

	#
	#
	############################################################################

	############################################################################
	#
	#

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
		
        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            if item:
                return item.person
		
        return QtCore.QVariant()

	#
	#
	############################################################################

	############################################################################
	#
	#

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
			role == QtCore.Qt.DisplayRole):
            try:
                return QtCore.QVariant(HORIZONTAL_HEADERS[column])
            except IndexError:
                pass
			
        return QtCore.QVariant()

	#
	#
	############################################################################

	############################################################################
	#
	#

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
		
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
		
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

	#
	#
	############################################################################

	############################################################################
	#
	#

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
		
        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()
        
        parentItem = childItem.parent()
		
        if parentItem == self.rootItem:
            return QtCore.QModelIndex()
		
        return self.createIndex(parentItem.row(), 0, parentItem)

	#
	#
	############################################################################

	############################################################################
	#
	#

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()
 
	#
	#
	############################################################################

	############################################################################
	#
	#

    def setupModelData(self):
        for target in self.target:
			objname = target.objname
			if not self.parents.has_key(objname):

				newparent = TreeItem(None, objname, self.rootItem)
				self.rootItem.appendChild(newparent)
				self.parents[objname] = newparent

			parentItem = self.parents[objname]
			newItem = TreeItem(target, "", parentItem)
			parentItem.appendChild(newItem)

	#
	#
	############################################################################

	############################################################################
	#
	#

    def newData(self,target):
		
		objname = target.objname
		if not self.parents.has_key(objname):

			newparent = TreeItem(None, objname, self.rootItem)
			self.rootItem.appendChild(newparent)
			self.parents[objname] = newparent

		parentItem = self.parents[objname]
		newItem = TreeItem(target, "", parentItem)
		parentItem.appendChild(newItem)

	#
	#
	############################################################################

	############################################################################
	#
	#

    def searchModel(self, person):
        '''
			get the modelIndex for a given appointment
			'''
        def searchNode(node):
            '''
				a function called recursively, looking at all nodes beneath node
				'''
            for child in node.childItems:
                if person == child.person:
                    index = self.createIndex(child.row(), 0, child)
                    return index
				
                if child.childCount() > 0:
                    result = searchNode(child)
                    if result:
                        return result
        
        retarg = searchNode(self.parents[0])
        print retarg
        return retarg

	#
	#
	############################################################################

	############################################################################
	#
	#

    def find_GivenName(self, fname):
        app = None
        for person in self.people:
            if person.fname == fname:
                app = person
                break
        if app != None:
            index = self.searchModel(app)
            return (True, index)
        return (False, None)

	#
	#
	############################################################################

#
#
################################################################################
