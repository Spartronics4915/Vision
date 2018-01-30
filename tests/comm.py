#
# comm:
#   manages our connection to the robot
#

from networktables import NetworkTables
import sys, traceback, time
import json
import logging

class Control:
    def __init__(self):
        self.targeting = None
        self.imuHeading = None

class Target:
    def __init__(self):
        self.clock = time.clock()
        self.angleX = 0
        self.angleY = 0

    def Send(self, targetTable):
        targetTable.putNumber("clock", self.clock)
        targetTable.putNumber("ax", self.angleX)
        targetTable.putNumber("ay", self.angleY)

VisionTableName = "Vision"
VisionControlTableName = "VisionControl"
theComm = None


def getVisionTable():
    return NetworkTables.getTable(VisionTableName)

def getVisionControlTable():
    return NetworkTables.getTable(VisionControlTableName)

class Comm:
    def __init__(self, serverIP):
        try:
            # IPAddress can be 
            #   - ip: "10.49.15.2" or 
            #   - name: "roboRIO-4915-FRC", "localhost"
            NetworkTables.initialize(server=serverIP)
            NetworkTables.setUpdateRate(.01)  
            # default is .05 (50ms/20Hz), .01 (10ms/100Hz)

            #self.sd = NetworkTables.getTable("SmartDashboard")

            # We communcate target to robot via Vision table,
            # current thinking is that this should not be a subtable of
            # SmartDashboard, since traffic is multiplied by the number
            # of clients.
            self.targetTable = getVisionTable()
            
            # robot communicates to us via fields within the Vision/Control 
            #  SubTable we opt for a different table to ensure we 
            #  receive callbacks from our own writes.
            self.controlTable = getVisionControlTable()
            self.controlTable.addConnectionListener(self.connectionListener)
            self.controlTable.addTableListener(self.visionControlEvent)

            self.control = Control()
            self.target = Target()

            self.fpsHistory = []
            self.lastUpdate = time.time()
            theComm = self

        except:
            xcpt = sys.exc_info()
            print("ERROR initializing network tables", xcpt[0])
            traceback.print_tb(xcpt[2])

    def Shutdown(self):
        self.controlTable.removeConnectionListener(self.connectionListener)
        self.controlTable.removeTableListener(self.visionControlEvent)

    def SetTarget(self, t):
        self.target = t
        self.target.Send(self.targetTable)

    def GetTarget(self):
        return self.target

    def GetIMUHeading(self):
        return self.control.imuHeading

    def SetFPS(self, fps):
        self.fpsHistory.append(fps)
        self.fpsHistory = self.fpsHistory[-15*4:]
        if time.time() - self.lastUpdate > 5:
            self.targetState.SetFPS(sum(self.fpsHistory)/len(self.fpsHistory))
            self.lastUpdate = time.time()

    def controlEvent(self, key, value, isNew):
        if key == 'SetTarget':
        	self.control.targeting = value
        elif key == 'IMUHeading':
        	self.control.imuHeading = value
            #print(value)
        else:
        	print("Unexpected key in visValueChanged")

    @staticmethod
    def visionControlEvent(table, key, value, isNew):
        # This is where we can be woken up if the driver station 
        # (or robot) wants to talk to us. This method fires only
        # on changes to /SmartDashboard/Vision/*
        theComm.controlEvent(key, value, isNew)

    @staticmethod
    def connectionListener(connected, connectionInfo):
        logging.getLogger("nt").debug("connected: %d" % connected)
        logging.getLogger("nt").debug("info: %s" % json.dumps(connectionInfo))
