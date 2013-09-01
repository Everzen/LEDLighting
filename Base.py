
from PyQt4 import QtGui, QtCore
import ColourLineGraphicView
import math

  
class LED_ColourPicker(QtGui.QWidget):
    def __init__(self):
        super(LED_ColourPicker, self).__init__()
        self.setWindowTitle("Rotation")
        self.setGeometry(50,50, 600, 600)
        self.ColourPickerCircle = {"center" : [237, 240], "centerOffset": [20,16] , "radius": 210 , "filename": "images/ColorWheelSat_500.png"}
        self.initUI()
       
       
    def initUI(self):   

        vbox = QtGui.QVBoxLayout()
        self.view = ColourLineGraphicView.Colour_GraphicsView(self.ColourPickerCircle)
        # self.view.setBackgroundImage("images/ColorWheelSat_500.png")
   
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
