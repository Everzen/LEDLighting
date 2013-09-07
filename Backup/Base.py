
from PyQt4 import QtGui, QtCore
import ColourLineGraphicView
import math
import sys

class LED_ColourPicker(QtGui.QWidget):
    def __init__(self):
        super(LED_ColourPicker, self).__init__()
        self.setWindowTitle("LED Light Line Colour Picker")
        self.setGeometry(50,50, 600, 600)
        self.ColourPickerCircle = {"center" : [245, 245], "centerOffset": [20,16] , "radius": 210 , "filename": "images/ColorWheelSat_500.png"}
        self.iP = str(sys.argv[1])
        self.port = str(sys.argv[2])
        self.initUI()
       
       
    def initUI(self):   
        vbox = QtGui.QVBoxLayout()
        self.view = ColourLineGraphicView.Colour_GraphicsView(self.iP, self.port, self.ColourPickerCircle)

        vbox.addWidget(self.view)
        self.setLayout(vbox)
        
    
    def changeValue(self, value):
        self.view.rect.doRotate(value)     


app = QtGui.QApplication([])
ex = LED_ColourPicker()
ex.show()
app.exec_()
