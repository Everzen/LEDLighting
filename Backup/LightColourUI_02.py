#Source code for some common Maya/PyQt functions we will be using
import sys
import sip
import math
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)
from PyQt4 import QtGui, QtCore
#import maya.OpenMayaUI as apiUI
#############################################################################################################

# def getMayaWindow():
# 	"""
# 	Get the main Maya window as a QtGui.QMainWindow instance
# 	@return: QtGui.QMainWindow instance of the top level Maya windows
# 	"""
# 	ptr = apiUI.MQtUtil.mainWindow()
# 	if ptr is not None:
# 		return sip.wrapinstance(long(ptr), QtCore.QObject)

class colourGrab():
	"""Class to return a colour value from an x,y coordinate. Assumes circle of radius 1"""
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.radius = 1
		self.colour = [0,0,1]

	def setRadius(self,Rad):
		self.radius = Rad

	def getH(self):
		"""Function to find and return distance which is Hue"""
		hAngle = (math.atan2(self.y,self.x))/(2*math.pi)
		if self.y < 0:
			hAngle = 1 + hAngle	
		return hAngle

	def getS(self):
		"""Function to find and return distance which is Saturation"""
		sValue = math.sqrt((math.pow(self.x,2)) + (math.pow(self.y,2)))/self.radius
		return sValue

	def getHSV(self):
		"""Function to get the HSV value this value will always have a value of 1"""
		self.colour = [self.getH(), self.getS(),1]
		return self.colour



class ColPickGVItem(QtGui.QGraphicsPixmapItem):
    def __init__(self, parent = None):
        super(ColPickGVItem, self).__init__(parent)
        print "It is me :) "
	
	def itemChange(self, change, value):
		print "Item new position " + str(self.pos().y())
		return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
    	self.lastPoint = self.pos()
    	print str(self.lastPoint.x()) + ", " + str(self.lastPoint.y())
        print "Node pressed"
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        print "Node released"
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    # def mouseMoveEvent(self, point):
    # 	if self.pos().x() > 50:
    # 		print "moo"
	
	# def mouseMoveEvent(self, event):
	# 	"""Function to overider dragMoveEvent to check that text is being used"""
	# 	print "the cor"


##MAIN FUNCTIONALITY######################################################
from PyQt4 import uic
#If you put the .ui file for this example elsewhere, just change this path.
treeExample_form, treeExample_base = uic.loadUiType('N:/PersonalWork/Richard/RaspberryPi/PyQt/PyQtUis/LightColourUI_02.ui')
class TreeExample(treeExample_form, treeExample_base):
	def __init__(self, parent=None):
		super(TreeExample, self).__init__(parent)
		self.setupUi(self)
		self.circleCentreX = 246
		self.circleCentreY = 240
		self.circleRadius = 210
		colWheelImg = QtGui.QPixmap("images/ColorWheelSat_500.png")
		self.gv_Scene = QtGui.QGraphicsScene()
		self.gv_Scene.addPixmap(colWheelImg)
		self.myGraphicsView.setScene(self.gv_Scene)
		self.item =  ColPickGVItem()
		itemImg = QtGui.QPixmap("images/colPick_circle.png")
		self.item.setPixmap(itemImg)
		colPickItem = self.gv_Scene.addItem(self.item)
		self.item.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

		self.pB_printPos.clicked.connect(self.getColPickPos)



	def getColPickPos(self):
		HSVValue = colourGrab(self.item.x()-self.circleCentreX, -(self.item.y()-self.circleCentreY))
		HSVValue.setRadius(self.circleRadius)
		HSVCol = HSVValue.getHSV()
		print "x y : " + str(HSVValue.x) + " " + str(HSVValue.y)
		print "HSVCol is : " + str(HSVCol)
		self.lE_colPickPos.setText("ColPick Pos : " + str(HSVCol[0]) + " " + str(HSVCol[1]) + " 1")



####################################INITIATE CLASS##########################

def main():
	app=QtGui.QApplication(sys.argv)
	myClass = TreeExample()
	myClass.show()
	app.exec_()

if __name__=="__main__":
	main()
