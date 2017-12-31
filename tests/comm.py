#
# comm:
#   manages our connection to the robot
#

from networktables import NetworkTable
import sys, traceback, time
import json
import logging

class Control:
    def __init__(self):
        self.targeting = None
        self.imuHeading = None

class Target:
    def __init__(self):
        self.angleX = None
        self.angleY = None

theComm = None

class Comm:
    def __init__(self, receiverIP):
        try:
            # IPAddress can be static ip ("10.49.15.2" or name:"roboRIO-4915-FRC"/"localhost")
            NetworkTable.setUpdateRate(.010)  # default is .05 (50ms/20Hz)
            NetworkTable.setIPAddress(receiverIP)
            NetworkTable.setClientMode()
            NetworkTable.initialize()

            self.sd = NetworkTable.getTable("SmartDashboard")

            # we communcate target to robot via VisionTarget table
            self.targetTable = self.sd.getSubTable("VisionTarget")
            
            # robot communicates to us via fields within the VisionControl SubTable
            # we opt for a different table to ensure we to receive callbacks from our
            # own writes.
            self.controlTable = self.sd.getSubTable("VisionControl")
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
        self.targetState.SetFPS(0)
        self.visTable.removeTableListener(self.visValueChanged)
        self.visTable.removeConnectionListener(self.connectionListener)

    def SetTarget(self, t):
        self.targetTable.putNumber("ax", t.angleX);
        self.targetTable.putNumber("ay", t.angleY);
        self.target = t

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
