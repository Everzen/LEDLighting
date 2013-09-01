#!/usr/bin/python

# ZetCode Advanced PyQt4 tutorial 
#
# In this examaple, we rotate a 
# rectangle
#
# author: Jan Bodnar
# website: zetcode.com 
# last edited: June 2010


from PyQt4 import QtGui, QtCore
import ColourLineGraphicView

class Rectangle(QtGui.QGraphicsRectItem):
    def __init__(self,x,y,w,h):
        super(Rectangle, self).__init__(x, y, w, h)
        
        self.setBrush(QtGui.QColor(250, 50, 0))
        self.setPen(QtGui.QColor(250, 50, 0))
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setCursor(QtCore.Qt.SizeAllCursor)
        
        self.tx = 200
        self.ty = 200
        
        
    def doRotate(self, alfa):
        
        tr = QtGui.QTransform()
        tr.translate(self.tx, self.ty)
        tr.rotate(alfa)
        tr.translate(-self.tx, -self.ty)
        
        self.setTransform(tr)
               
        

class View(QtGui.QGraphicsView):
    def __init__(self):
        super(View, self).__init__()
             
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        
        self.initScene()
        
        
    def initScene(self):
     

        self.scene = QtGui.QGraphicsScene()
        self.setSceneRect(50, 50, 600, 600)  
             
        self.rect = Rectangle(50, 50, 100, 100)        
        self.scene.addItem(self.rect)

        self.setScene(self.scene)  


class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()
       
        self.setWindowTitle("Rotation")
        self.setGeometry(50,50, 600, 600)
       
        self.initUI()
       
       
    def initUI(self):   

        vbox = QtGui.QVBoxLayout()
        
        self.view = ColourLineGraphicView.Colour_GraphicsView()
        # colWheelImg = QtGui.QPixmap("images/ColorWheelSat_500.png")
        self.view.setBackgroundImage("images/ColorWheelSat_500.png")
        # self.view.scene().addPixmap(colWheelImg)   
        # self.view.scene().drawBackground(colWheelImg)
        
        sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        sld.setRange(-180, 180)
        
        self.connect(sld, QtCore.SIGNAL('valueChanged(int)'), 
                      self.changeValue)
        
        vbox.addWidget(self.view)
        vbox.addWidget(sld)
        self.setLayout(vbox)
        
    
    def changeValue(self, value):

        self.view.rect.doRotate(value)     


app = QtGui.QApplication([])
ex = Example()
ex.show()
app.exec_()
