#Source code for some common Maya/PyQt functions we will be using
import sys
import sip
import math
# import ColourLineGraphicView
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


class ColPickTest(QtGui.QGraphicsItem):
    def __init__(self, circleCentreX, circleCentreY, radius,  parent = None):
        super(ColPickTest, self).__init__(parent)
        self.circleCentreX = circleCentreX
        self.circleCentreY = circleCentreY
        self.radius = radius
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setPos(self.circleCentreX, self.circleCentreY)
        print "Test Class has start"
        # set move restriction rect for the item
        self.move_restrict_rect = QtGui.QGraphicsEllipseItem(40, 37, 2*self.radius, 2*self.radius)


    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.lightGray)
        painter.drawEllipse(-10, -10, 20, 20)
        gradient = QtGui.QRadialGradient(0, 0, 22)
        if option.state & QtGui.QStyle.State_Sunken: # selected
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkGreen).lighter(120))
        else:
            gradient.setColorAt(1, QtCore.Qt.blue)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawEllipse(-6, -6, 12, 12)

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust,
                             22 + adjust, 23 + adjust)

    def mouseMoveEvent(self, event):
        # check of mouse moved within the restricted area for the item 
        if self.move_restrict_rect.contains(event.scenePos()):
            QtGui.QGraphicsItem.mouseMoveEvent(self, event)


##MAIN FUNCTIONALITY######################################################
from PyQt4 import uic
#If you put the .ui file for this example elsewhere, just change this path.
LEDLine_form, LEDLine_base = uic.loadUiType('LightColourUI_02.ui')
class LEDLightLine(LEDLine_form, LEDLine_base):
	def __init__(self, parent=None):
		super(LEDLightLine, self).__init__(parent)
		self.circleCentreX = 246
		self.circleCentreY = 240
		self.circleRadius = 210
		colWheelImg = QtGui.QPixmap("images/ColorWheelSat_500.png")
		self.gv_Scene = QtGui.QGraphicsScene()
		self.gv_Scene.addPixmap(colWheelImg)
		# self.myGraphicsView.setScene(self.gv_Scene)
		# self.item =  ColPickGVItem(self.circleCentreX, self.circleCentreY, self.circleCentreX, self.circleCentreY, self.circleRadius)
		self.item = ColPickTest(self.circleCentreX, self.circleCentreY, self.circleRadius)
		# self.item.setPos(243, 239)
		itemImg = QtGui.QPixmap("images/colPick_circle.png")
		#self.item.setPixmap(itemImg)
		colPickItem = self.gv_Scene.addItem(self.item)
		self.item.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

		# self.pB_printPos.clicked.connect(self.getColPickPos)
		self.setupUi(self)



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
	myClass = LEDLightLine()
	myClass.show()
	app.exec_()

if __name__=="__main__":
	main()
