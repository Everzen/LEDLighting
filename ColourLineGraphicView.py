##############LEDLIGHTLines############################################
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
    # print "This is Vec : " + str(vec)
    return vec

def QPVec(npVec):
    """Converts an np array into a QPoint"""
    return QtCore.QPointF(npVec[0], npVec[1])


class RigCurveInfo():
    """A Class to capture how the """
    def __init__(self,startNode, endNode, targNode):
        self.startPos = npVec(startNode().pos())
        self.endPos = npVec(endNode().pos())
        self.targPos = npVec(targNode().pos())
        # print "self.startPos : " + str(self.startPos)
        # print "self.endPos : " + str(self.endPos)
        # print "self.targPos : " + str(self.targPos)

        self.dirVec = self.endPos - self.startPos
        # print "dirVec : " + str(self.dirVec)
        self.dirDist = np.linalg.norm(self.dirVec)
        # print "dirDist : " + str(self.dirDist)
        self.perpUnitVec = self.setPerpUnitVec()
        # print "perpUnitVec : " + str(self.perpUnitVec)

        self.targetVec = norm(self.targPos - self.startPos)
        self.targNodeDist = np.linalg.norm(self.targPos - self.endPos)
        self.perpSwing = np.dot(self.perpUnitVec, self.targetVec)
        # self.sideSwing = 1 

    def setPerpUnitVec(self):
        perpVec = np.cross([self.dirVec[0], self.dirVec[1], 1], [0,0,1])
        #Normalised perpendicular vector
        perpVec = np.array([perpVec[0],perpVec[1]]) 
        # print "PerpVec = " + str(perpVec)
        self.PerpUnitVec = norm(perpVec)
        return self.PerpUnitVec

    def getStartPos(self):
        return self.startPos

    def getEndPos(self):
        return self.endPos

    def getTargPos(self):
        return self.targPos

    def getDirVec(self):
        return self.dirVec

    def getDirDist(self):
        return self.dirDist

    def getperpUnitVec(self):
        return self.perpUnitVec 

    def getTargetVec(self):
        return self.targetVec

    def getTargetNodeDist(self):
        return self.targNodeDist

    def getPerpSwing(self):
        return self.perpSwing

    # def setSideSwing(self):
    #     targetVec = norm(self.targPos - self.startPos)
    #     perpSwing = np.dot(self.PerpUnitVec, self.targetVec)
    #     sideSwitch = 1 
    #     if perpSwing > 0: 
    #         sideSwitch = 1


class RigCurve(QtGui.QGraphicsItem):
    def __init__(self, color, controlNodes, parent=None, scene=None):
        super(RigCurve, self).__init__(parent, scene)
        self.selected = False
        self.color = color
        #Experimemting with setting up some weak references to the Control Nodes - Need to feed in Control Nodes! 
        # self.startNode = weakref.ref(controlNodes[0])
        # self.endNode = weakref.ref(controlNodes[1])
        # self.targNode = weakref.ref(controlNodes[2])
        self.nodeList = self.getNodeList(controlNodes)
        # print "NODE LIST : " + str(self.nodeList)
        # print "Ctrl Node Pos : " + str(self.startNode().pos())
        # print "Ctrl Node Pos : " + str(self.endNode().pos())
        # print "Ctrl Node Pos : " + str(self.targNode().pos())
        # self.startNode().addRigCurve(self)
        # self.endNode().addRigCurve(self)
        # self.targNode().addRigCurve(self)

        self.curveSwing = 0.25
        self.handlescale = 0.3
        self.secondHandleScale = 0.5
        self.addCurveLink()
        self.buildCurve()

    def getNodeList(self, controlNodes):
        """Function to collect and store control nodes as weak references"""
        self.nodeList = []
        if len(controlNodes) < 3: print "WARNING : There are less than 3 Control Nodes" 
        for n in controlNodes: 
            self.nodeList.append(weakref.ref(n))
        return self.nodeList

    def addCurveLink(self):
        for n in self.nodeList:
            n().addRigCurve(self)

    def set_selected(self, selected):
        self.selected = selected

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(self, painter, option, widget):
        painter.setPen(self.color)
        painter.setBrush(self.color)
        painter.strokePath(self.path, painter.pen())

    def buildCurve(self):
        """Function to build section of Bezier"""
        if len(self.nodeList) >= 3:
            self.path = QtGui.QPainterPath()
            self.prepareGeometryChange()
            #BuildSection
            curveInfo = RigCurveInfo(self.nodeList[0],self.nodeList[1],self.nodeList[2])
            startPoint = curveInfo.getStartPos()
            endPoint = curveInfo.getEndPos()
            targetPoint= curveInfo.getTargPos()
            #Take point at a 1/3 of the way along the line and 2/3 of the way along the line
            cP1 = startPoint + self.handlescale*curveInfo.getDirVec() - curveInfo.getDirDist()*curveInfo.getperpUnitVec()*self.curveSwing*curveInfo.getPerpSwing()
            cP2 = startPoint + (1-self.handlescale)*curveInfo.getDirVec() - curveInfo.getDirDist()*curveInfo.getperpUnitVec()*self.curveSwing*curveInfo.getPerpSwing()
            #Now make sure that we assign the new Bezier handles to the end node, but making the far handle proportional to the next segment length
            self.nodeList[0]().setBezierHandles(cP1, 1)
            self.nodeList[1]().setBezierHandles(cP2, 0)
            #Now calculate our endNode second handle - to do this we need to calculate the distance to the next node (endnode to targetnode)
            targNodeDist = np.linalg.norm(targetPoint - endPoint)
            #Now set the next handle of the endpoint to be the same tangent, but scaled in proportion to the length of the endnode -> targetnode segment 
            cPNext = (endPoint - cP2)*self.secondHandleScale*curveInfo.getTargetNodeDist()/curveInfo.getDirDist() + endPoint
            self.nodeList[1]().setBezierHandles(cPNext, 1)
            # print "End Node Handle Test : " + str(self.nodeList[1]().getBezierHandles(0))
            # print "End Node Handle Test : " + str(self.nodeList[1]().getBezierHandles(1))
            # print "CP1 : " + str(cP1)
            # print "CP2 : " + str(cP2)
            #Move the points out along the the perpendicular vector by a 3rd of the magnitude
            self.path.moveTo(QPVec(startPoint))
            self.path.cubicTo(QPVec(cP1),QPVec(cP2),QPVec(endPoint))
            # self.path.cubicTo(QPVec([20,20]),QPVec([40,20]),QPVec([50,50]))
            midNodes = self.nodeList[1:-2]
            for index,node in enumerate(midNodes): #This is setup to give us nodes and indexing
                curveInfo = RigCurveInfo(node,self.nodeList[index+2],self.nodeList[index+3])
                startPoint = curveInfo.getStartPos()
                endPoint = curveInfo.getEndPos()
                targetPoint= curveInfo.getTargPos()
                #First Control Point is already resolved!
                cP1 = node().getBezierHandles(1)
                cP2 = startPoint + (1-self.handlescale)*curveInfo.getDirVec() - curveInfo.getDirDist()*curveInfo.getperpUnitVec()*self.curveSwing*curveInfo.getPerpSwing()

                node().setBezierHandles(cP1, 1)
                self.nodeList[index+2]().setBezierHandles(cP2, 0)
                #Now figure out next node hand
                targNodeDist = np.linalg.norm(targetPoint - endPoint)
                cPNext = (endPoint - cP2)*self.secondHandleScale*curveInfo.getTargetNodeDist()/curveInfo.getDirDist() + endPoint
                self.nodeList[index+2]().setBezierHandles(cPNext, 1)
                self.path.cubicTo(QPVec(cP1),QPVec(cP2),QPVec(endPoint))
            #Now place the final Bezier. To do this we will calculate from the end backwards, then plot the nodes forwards
            curveInfo = RigCurveInfo(self.nodeList[-1],self.nodeList[-2],self.nodeList[-3])
            startPoint = curveInfo.getStartPos()
            endPoint = curveInfo.getEndPos()
            targetPoint= curveInfo.getTargPos()
            cP2 = startPoint + self.handlescale*curveInfo.getDirVec() - curveInfo.getDirDist()*curveInfo.getperpUnitVec()*self.curveSwing*curveInfo.getPerpSwing()
            #We have cP1 from our previous Node calculations
            cP1 = self.nodeList[-2]().getBezierHandles(1)
            self.nodeList[-1]().setBezierHandles(cP2, 0)
            self.path.cubicTo(QPVec(cP1),QPVec(cP2),QPVec(startPoint))


###Nodes for selection in the Graphics View
class Node(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 1

    def __init__(self, graphWidget, xPos, yPos):
        QtGui.QGraphicsItem.__init__(self)

        self.graph = weakref.ref(graphWidget)
        self.rigCurveList = []
        self.bezierHandles = [None, None]
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

    def addRigCurve(self, rigCurve):
        self.rigCurveList.append(weakref.ref(rigCurve))
        # print "Rig Curve List is : " + str(self.rigCurveList) + " - for Node :" + str(self)

    def setBezierHandles(self, handlePos, handleNo):
        """A function to record the position of the bezier handles associated with this Node"""
        self.bezierHandles[handleNo] = handlePos

    def getBezierHandles(self, handleNo):
        """A function to return the position of the bezier handles associated with this Node"""
        return self.bezierHandles[handleNo]

    def set_index(self, index):
        self.index = index
        self.label = "Step %d" % index
        self.setToolTip(self.label)

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
            for rigCurve in self.rigCurveList:
                rigCurve().buildCurve()
        # print "Item new position :" + str(self.pos().x()) + ", " + str(self.pos().y())
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        if not self.graph().inhibit_edit:
            self.update()
            # print "Node pressed"
            QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if not self.graph().inhibit_edit:
            self.update()
            print "Node Pos: " + str(self.pos())
            #
            QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

###
class Colour_GraphicsView(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self) 

        self.size = (0, 0, 600, 500)
        self.img = None
        #
        policy = QtCore.Qt.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(policy)
        self.setHorizontalScrollBarPolicy(policy)

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
        self.scale(1,1)
        self.setMinimumSize(600, 400)
        self.setWindowTitle(self.tr("Elastic Nodes"))
        self.inhibit_edit = False
        # self.add_curve()
        # self.addRigControl([[20,20],[265,66],[325,205],[200,400],[100,200],[250,400],[650,300]])
        self.addRigControl([[290,80],[384,137],[424,237],[381,354]])

        # self.addRigControl([[150,150],[365,120],[600,250],[300,400]])

    def setBackgroundImage(self,imagepath):
        self.img = imagepath

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
        return node

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
        # print "GraphWidget mouse"
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

    def drawBackground(self, painter, rect):
        if self.img != None:
            backImage = QtGui.QPixmap(self.img)
            backImage.scaled(600,600, QtCore.Qt.KeepAspectRatio)
            painter.drawPixmap(rect, backImage, rect)
            # print "This was drawn"
        sceneRect = self.sceneRect()
        # print "Back image is: " + str(self.img)

    def addRigControl(self, controlPosList, color = QtGui.QColor(255, 0, 0)):
        scene = self.scene()
        rigCurveNodes = []
        for p in controlPosList:
            newNode = self.add_node(p[0],p[1])
            # ctrlPoint = QtCore.QPointF(p[0], p[1])
            rigCurveNodes.append(newNode)
            # rigCurveNodes.append(ctrlPoint)
        # print "Node List : " + str(rigCurveNodes)
        # for n in rigCurveNodes: print "Node Pos : " + str(n.pos())
        curve = RigCurve(color, rigCurveNodes)
        scene.addItem(curve)
