##############LEDLIGHTLines############################################
import sys
import weakref
import math
from PyQt4 import QtCore, QtGui
import numpy as np
import socket #for sending out UPD signals

#######


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


class ColourBroadcaster():
    def __init__(self, iP, port):
        self.colourGrabberList = []
        self.broadcastColourStr = ""
        self.host = "192.168.1."
        if iP == "localhost": self.host = iP     #Catch the condition where we are working with a local host
        else: self.host += str(iP)
        self.port = port
        #create new socket from the socket library - with IP address system (IPv4),  protocol (UDP)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def addColourGrab(self,colourGrabber):
        self.colourGrabberList.append(colourGrabber)

    def setValue(self , value):
        for c in self.colourGrabberList:
            c.setValue(round(value,2))

    def broadcast(self):
        self.broadcastColourStr = ""
        for index,c in enumerate(self.colourGrabberList):
            if c != self.colourGrabberList[-1]: self.broadcastColourStr += str(c.getColour()) + "|" #not dealing with last element
            else: self.broadcastColourStr += str(c.getColour()) # dealing with last element
        # print "HOST : %s PORT : %s" % (str(self.host), str(self.port))
        if len(self.colourGrabberList) == 4:
            print "BroadCast String is : " + self.broadcastColourStr
            self.socket.sendto(self.broadcastColourStr, (self.host, int(self.port)))
        return self.broadcastColourStr


class colourGrab():
    """Class to return a colour value from an x,y coordinate. Assumes circle of radius 1"""
    def __init__(self,colourBroadcaster, radius=1, hThreshold = 0.01, sThreshold = 0.03):
        self.x = None
        self.y = None
        self.radius = radius
        self.sThreshold = sThreshold
        self.hThreshold = hThreshold
        self.colour = [0,0,1]
        self.currentColour = [0,0,1]
        self.colourBroadcaster = colourBroadcaster
        self.index = 0

    def setIndex(self, value):
        self.index = value

    def getIndex(self):
        return self.index

    def setPos(self,nodePos):
        self.x = nodePos[0]
        self.y = nodePos[1]
        print "Node Pos " + str(self.index) + ": " + str(self.x) + "," + str(self.y)

    def setRadius(self,Rad):
        self.radius = Rad

    def setThreshold(self,threshold):
        self.threshold = threshold

    def getH(self):
        """Function to find and return distance which is Hue"""
        hAngle = (math.atan2(self.y,self.x))/(2*math.pi)
        if self.y < 0:
            hAngle = 1 + hAngle 
        return round(hAngle,2)

    def getS(self):
        """Function to find and return distance which is Saturation"""
        sValue = math.sqrt((math.pow(self.x,2)) + (math.pow(self.y,2)))/self.radius
        return round(sValue,2)

    def getV(self):
        pass

    def setValue(self,value):
        self.colour[2] = value

    def getHSV(self):
        """Function to get the HSV value this value will always have a value of 1"""
        colour = [self.getH(), self.getS(), self.colour[2]]
        return colour

    def getDifference(self,colour):
        if math.fabs(colour[0] - self.colour[0]) > self.hThreshold or math.fabs(colour[1] - self.colour[1]) > self.sThreshold:
            return True
        else: False

    def getColour(self):
        return self.colour

    def mouseMoveExecute(self):
        """This is the class to broadcast UDP data out"""
        newColour = self.getHSV()
        if self.getDifference(newColour):
            self.colour = newColour
            self.currentColour = newColour
            self.colourBroadcaster.broadcast()
            print "New colour returning : " + str(self.currentColour) 
            return self.colour
            # print " The colour has been updated to : " + str(self.colour)
        else:
            # print "Difference is not enough to change colour"
            print "Current colour returning : " + str(self.currentColour)  
            return self.currentColour



class colourValueSliderControl(QtGui.QGraphicsItem):
    def __init__(self,colourBroadcaster):
        super(colourValueSliderControl, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.maxLevel = 447.7
        self.minLevel = 40.7  
        self.currentValue = 1
        self.threshold = 0.02  
        self.setPos(QtCore.QPointF(509.75,40.7))
        self.move_restrict_rect = QtGui.QGraphicsRectItem(509,40,2,410)
        self.colourBroadcaster = colourBroadcaster #Pass the slider a Broadcaster

    def boundingRect(self):
        adjust = 0.0
        return QtCore.QRectF(-18 - adjust, -4 - adjust,
                             36 + adjust, 8 + adjust)

    def paint(self, painter, option, widget):
        # painter.drawLine(QtCore.QLineF(6,-40,6,-2))
        painter.setPen(QtCore.Qt.NoPen)
        painter.setPen(QtGui.QPen(QtCore.Qt.lightGray, 0))
        painter.drawRect(-16, -4, 33, 8)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawRect(-12.5, -2.75, 25, 5)
        pen = QtGui.QPen(QtCore.Qt.red, 0.5, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(-21.5,0,43,0)

    def getValue(self, yPos):
        """A function to return the """
        range = self.minLevel - self.maxLevel
        portion = yPos - self.minLevel
        value = float(1- math.fabs(portion/range))
        if math.fabs(self.currentValue - value) > self.threshold: #check to see if there has been a big enough change
            self.currentValue = value
            return value
        # else:
            # print "Value difference is not enough"

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            # print "Item new position :" + str(self.pos().x()) + ", " + str(self.pos().y())
            # print "Max Level : " + str(self.maxLevel)
            yPos = value.toPointF().y()
            if yPos > self.maxLevel : yPos = self.maxLevel
            elif yPos < self.minLevel : yPos = self.minLevel
            vValue = self.getValue(yPos)
            # print "VValue %s" % str(vValue)
            if vValue:       
                self.colourBroadcaster.setValue(vValue)
                self.colourBroadcaster.broadcast()
                # print "Colour Value is : " + str(self.getValue(yPos))
            return QtCore.QPointF(509.75,yPos)
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mouseMoveEvent(self, event):
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)

        

class colourValueSliderBackGround(QtGui.QGraphicsItem):
    def __init__(self):
        super(colourValueSliderBackGround, self).__init__()
        #VALUE SLIDER
        self.brush = None
        self.createSlider()
        # self.slider.setBrush(g)

    def createSlider(self):
        self.gradStart = QtCore.QPointF(500,40)
        self.gradEnd = QtCore.QPointF(500,450)
        self.gradient = QtGui.QLinearGradient(self.gradStart, self.gradEnd)
        self.gradient.setColorAt(1.0, QtGui.QColor(0,0,0))
        self.gradient.setColorAt(0.0, QtGui.QColor(255,255,255))

    def paint(self, painter, option, widget):
        painter.drawRect(500,40,20,410)
        painter.fillRect(500,40,20,410,self.gradient)
        # painter.setBrush(self.gradient)

    def boundingRect(self):
        return QtCore.QRectF(500,40,20,410)


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



class RigCurve(QtGui.QGraphicsItem):
    def __init__(self, color, controlNodes, parent=None, scene=None):
        super(RigCurve, self).__init__(parent, scene)
        self.selected = False
        self.color = color
        self.nodeList = self.getNodeList(controlNodes)
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
        pen = QtGui.QPen(QtCore.Qt.black, 1.2, QtCore.Qt.DotLine)
        painter.setPen(pen)
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
    def __init__(self, graphWidget, xPos, yPos, circleDefinition=None, moveThreshold=5, operatorClass = None):
        QtGui.QGraphicsItem.__init__(self)
        self.index = 0
        self.graph = weakref.ref(graphWidget)
        self.rigCurveList = []
        self.bezierHandles = [None, None]
        self.newPos = QtCore.QPointF()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)
        self.circleDefinition = circleDefinition
        self.move_restrict_circle = None
        self.operatorClass = operatorClass
        self.setPos(xPos,yPos)
        self.marker = False
        if self.circleDefinition:
            self.move_restrict_circle = QtGui.QGraphicsEllipseItem(2*self.circleDefinition["centerOffset"][0],2*self.circleDefinition["centerOffset"][1], 2*self.circleDefinition["radius"],2*self.circleDefinition["radius"])
        offsetPos = self.pos() - QPVec(self.circleDefinition["center"])
        self.operatorClass.setPos([offsetPos.x(),offsetPos.y()]) #Set colourGrabber position
        self.operatorClass.mouseMoveExecute() # Set the initial colour

    def setIndex(self,value):
        self.index = value

    def getIndex(self):
        return self.index

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

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust,
                             22 + adjust, 23 + adjust)

    def paint(self, painter, option, widget):
        # painter.drawLine(QtCore.QLineF(6,-40,6,-2))
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
            # print "Node Pos: " + str(self.pos())
            QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        # check of mouse moved within the restricted area for the item 
        if self.circleDefinition:
            if self.move_restrict_circle.contains(event.scenePos()):
                QtGui.QGraphicsItem.mouseMoveEvent(self, event)
                if self.operatorClass:
                    nodePos = self.pos() - QPVec(self.circleDefinition["center"])
                    # print "Node Pos " + str(self.index) + ": " + str(nodePos.x()) + "," + str(nodePos.y())
                    self.operatorClass.setPos(npVec(nodePos))
                    self.operatorClass.mouseMoveExecute() #Execute our defined operator class through the move event
        else: QtGui.QGraphicsItem.mouseMoveEvent(self, event)

###
class Colour_GraphicsView(QtGui.QGraphicsView):
    def __init__(self, iP, port, circleDefinition):
        QtGui.QGraphicsView.__init__(self) 
        self.size = (0, 0, 600, 500)
        self.img = None
        self.circleDefinition = circleDefinition
        self.iP = iP
        self.port = port
        self.colourBroadCaster = ColourBroadcaster(self.iP,self.port)
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
        self.setBackgroundImage(self.circleDefinition["filename"])
        # self.add_curve()
        # self.addRigControl([[20,20],[265,66],[325,205],[200,400],[100,200],[250,400],[650,300]])
        self.addRigControl([[290,80],[384,137],[424,237],[381,354]])

        #Value Slider
        self.valueSliderBackground = colourValueSliderBackGround()
        scene.addItem(self.valueSliderBackground)

        self.colourValueSliderControl = colourValueSliderControl(self.colourBroadCaster )
        scene.addItem(self.colourValueSliderControl)





    def setBackgroundImage(self,imagepath):
        self.img = imagepath

    def calc_upper_limits(self):
        self.toptemp = (self.maxtemp / 100 + 1) * 100
        self.toptime = (int(self.maxtime) / 30 + 1) * 30
        self.graph_width_ratio = float(self.size[2]) /self.toptime
        self.graph_height_ratio = float(self.size[3]) / self.toptemp

    def add_node(self,xPos,yPos, marker=False):
        scene = self.scene()
        # Insert Node into scene
        colourGrabber = colourGrab(self.colourBroadCaster, radius = self.circleDefinition["radius"])
        node = Node(self, xPos, yPos, circleDefinition =  self.circleDefinition, operatorClass = colourGrabber)
        node.setIndex(self.nodecount)
        colourGrabber.setIndex(self.nodecount) #Make sure that the Node and the ColourGrabber have neatly setup indexes
        self.colourBroadCaster.addColourGrab(colourGrabber) #Make sure that the colour grabber is past to the broadcaster
        scene.addItem(node)
        self.nodecount += 1
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

    def addRigControl(self, controlPosList, color = QtGui.QColor(0, 0, 0)):
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
