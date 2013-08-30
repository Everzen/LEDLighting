# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LightColourUI_00.ui'
#
# Created: Mon Jul 15 19:22:27 2013
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!
import sys
from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_lightColourDialog(QtGui.QWidget):
    def __init__(self):
        super(Ui_lightColourDialog, self).__init__()
        
        self.setupUi()

    def setupUi(self):
        #lightColourDialog.setObjectName(_fromUtf8("lightColourDialog"))
        #lightColourDialog.resize(415, 372)
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setGeometry(QtCore.QRect(150, 340, 261, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.listView = QtGui.QListView()
        self.listView.setGeometry(QtCore.QRect(10, 10, 261, 192))
        self.listView.setObjectName(_fromUtf8("listView"))

        #self.retranslateUi(lightColourDialog)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), lightColourDialog.accept)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), lightColourDialog.reject)
        #QtCore.QMetaObject.connectSlotsByName(lightColourDialog)

    def retranslateUi(self, lightColourDialog):
        lightColourDialog.setWindowTitle(_translate("lightColourDialog", "Light Colour Dialog", None))


def main():
    app =QtGui.QApplication(sys.argv)
    myClass = Ui_lightColourDialog()
    myClass.show()
    app.exec_()

if __name__=="__main__":
    main()
