import sys
from PyQt4 import QtGui, QtCore

class TestEclipseItem(QtGui.QGraphicsEllipseItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsPixmapItem.__init__(self, parent)

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)

        # set move restriction rect for the item
        self.move_restrict_rect = QtCore.QRectF(20, 20, 200, 200)
        # set item's rectangle
        self.setRect(QtCore.QRectF(50, 50, 50, 50))

    def mouseMoveEvent(self, event):
        # check of mouse moved within the restricted area for the item 
        if self.move_restrict_rect.contains(event.scenePos()):
            QtGui.QGraphicsEllipseItem.mouseMoveEvent(self, event)

class MainForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        scene = QtGui.QGraphicsScene(-50, -50, 600, 600)

        ellipseItem = TestEclipseItem()
        scene.addItem(ellipseItem)

        view = QtGui.QGraphicsView()
        view.setScene(scene)
        view.setGeometry(QtCore.QRect(0, 0, 400, 200))
        self.setCentralWidget(view)

def main():
    app = QtGui.QApplication(sys.argv)
    form = MainForm()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()