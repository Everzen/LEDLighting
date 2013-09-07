import sys
import weakref
import math
from PyQt4 import QtCore, QtGui
import numpy as np

def norm(vec):
    """function to normalise a vector - creating the unit vector"""
    return vec/np.linalg.norm(vec)

def npVec(vec):
    """Converts a list/QPoint into an np array"""
    vec = np.array([vec.x(),vec.y()])
    print "This is Vec : " + str(vec)
    return vec

def QPVec(npVec):
    """Converts an np array into a QPoint"""
    return QtCore.QPointF(npVec[0], npVec[1])

class RigCurve(QtGui.QGraphicsItem):
    def __init__(self, color, control_points, parent=None, scene=None):
        super(RigCurve, self).__init__(parent, scene)
        self.selected = False
        self.color = color
        self.controlPoints = control_points
        self.path = QtGui.QPainterPath()
        self.curveSwing = 0.25
        # self.path.moveTo(control_points[0])
        # self.path.cubicTo(*control_points[1:])
        self.buildSection()

    def set_selected(self, selected):
        self.selected = selected

    def contains_point(self, x, y, epsilon):
        p = (x, y)
        min_distance = float(0x7fffffff)
        t = 0.0
        while t < 1.0:
            point = self.path.pointAtPercent(t)
            spline_point = (point.x(), point.y())
            print p, spline_point
            distance = self.distance(p, spline_point)
            if distance < min_distance:
                min_distance = distance
            t += 0.1
        print min_distance, epsilon
        return (min_distance <= epsilon)

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(self, painter, option, widget):
        painter.setPen(self.color)
        painter.setBrush(self.color)
        painter.strokePath(self.path, painter.pen())

    def distance(self, p0, p1):
        a = p1[0] - p0[0]
        b = p1[1] - p0[1]
        return sqrt(a * a + b * b)

    def buildSection(self):
        """Function to build section of Bezier"""
        #This is now working for an individual section, we need to continue the philosphy to a general number of points!
        startPoint = npVec(self.controlPoints[0])
        endPoint = npVec(self.controlPoints[1])
        targetPoint = npVec(self.controlPoints[1])
        #Now establish the perpendicular vector
        dirVec = endPoint - startPoint
        dirDist = np.linalg.norm(dirVec)
        perpVec = np.cross([dirVec[0], dirVec[1], 1], [0,0,1])
        #Normalised perpendicular vector
        perpVec = np.array([perpVec[0],perpVec[1]]) 
        print "PerpVec = " + str(perpVec)
        perpVec = norm(perpVec)
        targetVec = targetPoint - startPoint
        sideSwitch = 1 
        if np.dot(perpVec, targetVec) < 0: 
            sideSwitch = -1
        #Take point at a 1/3 of the way along the line and 2/3 of the way along the line
        cP1 = startPoint + sideSwitch*dirVec/3 + dirDist*perpVec*self.curveSwing
        cP2 = startPoint + sideSwitch*2*dirVec/3 + dirDist*perpVec*self.curveSwing
        #Move the points out along the the perpendicular vector by a 3rd of the magnitude
        self.path.moveTo(QPVec(startPoint))
        self.path.cubicTo(QPVec(cP1),QPVec(cP2),QPVec(endPoint))


###
class Edge(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        QtGui.QGraphicsItem.__init__(self)
        #
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.source = weakref.ref(sourceNode)
        self.dest = weakref.ref(destNode)
        self.source().addEdge(self)
        self.dest().addEdge(self)
        self.set_index()
        self.adjust()

    def type(self):
        return Edge.Type

    def sourceNode(self):
        return self.source()

    def setSourceNode(self, node):
        self.source = weakref.ref(node)
        self.adjust()

    def destNode(self):
        return self.dest()

    def setDestNode(self, node):
        self.dest = weakref.ref(node)
        self.adjust()

    def set_index(self):
        self.setToolTip(self.source().label)

    def adjust(self):
        # do we have a line to draw ?
        if  self.source() and self.dest():
            line = QtCore.QLineF(self.mapFromItem(self.source(), 0, 0), self.mapFromItem(self.dest(), 0, 0))
            length = line.length()
            if length > 20:
                edgeOffset = QtCore.QPointF((line.dx() * 10) / length, (line.dy() * 10) / length)
                self.prepareGeometryChange()
                self.sourcePoint = line.p1() + edgeOffset
                self.destPoint   = line.p2() - edgeOffset
            else: # want to make sure line not drawn
                self.prepareGeometryChange()
                self.sourcePoint = self.destPoint 

    def boundingRect(self):
        # do we have a line to draw ?
        if not self.source() or not self.dest():
            return QtCore.QRectF()
        else:
            extra = 1
            return QtCore.QRectF(self.sourcePoint,
                                 QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                                               self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        if self.source() and self.dest():
            # Draw the line itself.
            line = QtCore.QLineF(self.sourcePoint, self.destPoint)
            if line.length() > 0.0:
                painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                painter.drawLine(line)

###
class Node(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 1

    def __init__(self, graphWidget, xPos, yPos):
        QtGui.QGraphicsItem.__init__(self)

        self.graph = weakref.ref(graphWidget)
        self.edgeList = []
        self.set_index(-1)
        self.newPos = QtCore.QPointF()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)
        #
        # self.temp = temp
        # self.time = time
        # x,y = self.map_temptime_to_pos()
        self.setPos(xPos,yPos)
        self.marker = False




    def type(self):
        return Node.Type

    def addEdge(self, edge):
        self.edgeList.append(weakref.ref(edge))

    def set_index(self, index):
        self.index = index
        self.label = "Step %d" % index
        self.setToolTip(self.label)

    def get_prev_edge(self):
        index = 1000
        edge = False
        for e in self.edgeList:
            sn = e().source().index
            dn = e().dest().index
            if sn < index:
                index = sn
                edge = e
            if dn < index:
                index = dn
                edge = e
        return edge

    def get_next_edge(self):
        index = -1
        edge = False
        for e in self.edgeList:
            sn = e().source().index
            dn = e().dest().index
            if sn > index:
                index = sn
                edge = e
            if dn > index:
                index = dn
                edge = e
        return edge

    def map_temptime_to_pos(self):
        x = self.time * self.graph().graph_width_ratio
        y = self.graph().size[3] - self.temp * self.graph().graph_height_ratio
        return (x,y)

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust,
                             22 + adjust, 23 + adjust)

    def paint(self, painter, option, widget):
        painter.drawLine(QtCore.QLineF(6,-40,6,-2))
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


    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for edge in self.edgeList:
                edge().adjust()

        if self.pos().y() < 25:
            self.setPos(self.pos().x(),25)
        print "Item new position :" + str(self.pos().x()) + ", " + str(self.pos().y())
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        if not self.graph().inhibit_edit:
            self.update()
            print "Node pressed"
            QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if not self.graph().inhibit_edit:
            self.update()
            print "Node released"
            #
            QtGui.QGraphicsItem.mouseReleaseEvent(self, event)



###
class GraphWidget(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)
        self.size = (-30, 30, 600, 400)
        #
        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        scene.setSceneRect(self.size[0],self.size[1],self.size[2],self.size[3])
        self.setScene(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        #
        self.maxtemp = 300
        self.maxtime = 160
        self.nodecount = 0
        self.calc_upper_limits()
        #
        self.scale(0.8, 0.8)
        self.setMinimumSize(600, 400)
        self.setWindowTitle(self.tr("Elastic Nodes"))
        self.inhibit_edit = False
        # self.add_curve()
        self.addRigControl([[20,20],[265,66],[325,205],[200,400]])

    def calc_upper_limits(self):
        self.toptemp = (self.maxtemp / 100 + 1) * 100
        self.toptime = (int(self.maxtime) / 30 + 1) * 30
        self.graph_width_ratio = float(self.size[2]) /self.toptime
        self.graph_height_ratio = float(self.size[3]) / self.toptemp

    def add_node(self,xPos,yPos, marker=False):
        self.nodecount += 1
        scene = self.scene()
        # Insert Node into scene
        node = Node(self, xPos, yPos)
        scene.addItem(node)
        # Insert new edges
        nodes = self.get_ordered_nodes()
        if len(nodes) > 1:
            e = Edge(nodes[-2], node)
            scene.addItem(e)
        # cleanup edge tooltips
        for n in self.get_ordered_nodes():
            edges = n.edgeList
            for e in edges:
                e().set_index()

    def get_ordered_nodes(self):
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]
        nodes.sort(key=lambda n: n.index)
        return nodes

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == QtCore.Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)

    def mousePressEvent(self, event):
        print "GraphWidget mouse"
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

    def drawBackground(self, painter, rect):
        sceneRect = self.sceneRect()

    def addRigControl(self, controlPosList, color = QtGui.QColor(255, 0, 0)):
        scene = self.scene()
        rigCurvePoints = []
        for p in controlPosList:
            self.add_node(p[0],p[1])
            ctrlPoint = QtCore.QPointF(p[0], p[1])
            rigCurvePoints.append(ctrlPoint)
            # rigCurvePoints.append(ctrlPoint)

        curve = RigCurve(color, rigCurvePoints)
        scene.addItem(curve)

    def add_curve(self):
        scene = self.scene()
        color = QtGui.QColor(255, 0, 0)
        x0 = 10.0
        y0 = 10.0
        x1 = 30.0
        y1 = 20.0
        x2 = 60.0
        y2 = 10.0
        x3 = 100.0
        y3 = 100.0
        control_points = (QtCore.QPointF(x0, y0), QtCore.QPointF(x1, y1),
            QtCore.QPointF(x2, y2), QtCore.QPointF(x3, y3))
        curve = RigCurve(color, control_points)
        scene.addItem(curve)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    widget = GraphWidget()
    widget.show()
    sys.exit(app.exec_())