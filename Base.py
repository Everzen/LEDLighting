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
      
class LED_ColourPicker(QtGui.QWidget):
    def __init__(self):
        super(LED_ColourPicker, self).__init__()
        self.setWindowTitle("Rotation")
        self.setGeometry(50,50, 600, 600)
        self.initUI()
       
       
    def initUI(self):   

        vbox = QtGui.QVBoxLayout()
        self.view = ColourLineGraphicView.Colour_GraphicsView()
        self.view.setBackgroundImage("images/ColorWheelSat_500.png")
   
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
ex = LED_ColourPicker()
ex.show()
app.exec_()
