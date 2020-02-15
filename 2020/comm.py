# comm:
#   manages our connection to the robot
#

from networktables import NetworkTables
import sys, traceback, time
import json
import logging
import re

class Control:
    """
        Control signals are sent by robot or driver station,
        Received by vision processor to guide its behavior.
    """
    def __init__(self):
        self.targeting = None
        self.imuHeading = None

theComm = None

# Abstractions to ensure that a Comm has been created 
def PutString(key, value):
    if theComm != None:
        theComm.sd.putString("Vision/"+key, value)

def PutNumberArray(key, value):
    if theComm != None:
        theComm.sd.putNumberArray("Vision/"+key, value)

def getCurrentTime():
    if theComm != None:
        # Get the current time
        timestamp = theComm.robotTable.getNumber("timestamp",(-1))
        return timestamp # x,y,time

def getCameraPosition():
    if theComm != None:
        # Get the robot relative mounting of the camera
        mountPosition = theComm.controlTable.getNumberArray("mountIntrensics",-1)
        return mountPosition # x,y,z

def getTurretAngle():
    if theComm != None:
        # Get the turret angle from smartDashboard
        # TODO Check
        turretTheta = theComm.controlTable.getNumber("turretAngle",-1)
        return turretTheta

class Comm:
    """
        Comm abstracts our network-tables conventions.
        Can be instantiated either by the vision processor or
        by the fake robot server.
    """
    def __init__(self, serverIP):
        global theComm
        try:
            # IPAddress can be
            #   - None: means run as fake server
            #   - ip: "10.49.15.2" or
            #   - name: "roboRIO-4915-FRC", "localhost"
            if serverIP != None:
                # we're a client
                self.asServer = False
                NetworkTables.initialize(server=serverIP)
                # don't override updaterate as it apparently causes
                # odd behavior.
            else:
                # we're fake server
                self.asServer = True
                NetworkTables.initialize()

            theComm = self # for callback access

            # update the dashboard with our state, NB: this is a different table
            # that both the vision and control tables.
            self.sd = NetworkTables.getTable("SmartDashboard")
            self.sd.putString("Vision/Status", "Connected")
            self.UpdateVisionState("Standby")

            # We communicate target to robot via Vision table.
            self.controlTable = NetworkTables.getTable("/VisionControl")
            self.robotTable =  NetworkTables.getTable("SmartDashboard/RobotState") #XXX: Might not work
            self.control = Control()

            # Robot communicates to us via fields within the Vision/Control
            #  SubTable we opt for a different table to ensure we
            #  receive callbacks from our own writes.
            if self.asServer:
                # as server, we're interested in reporting connections
                NetworkTables.addConnectionListener(self.connectionListener,
                                                    immediateNotify=True)
            else:
                # as vision controller, we're interested in acting upon
                # vision control events.
                self.controlTable.addEntryListener(self.visionControlEvent)

        except:
            xcpt = sys.exc_info()
            logging.info("ERROR initializing network tables", xcpt[0])
            traceback.print_tb(xcpt[2])

    def UpdateVisionState(self, state):
        self.sd.putString("Vision/State", state)

    def Shutdown(self):
        NetworkTables.removeConnectionListener(self.connectionListener)
        self.controlTable.removeEntryListener(self.visionControlEvent)

    def GetIMUHeading(self):
        return self.control.imuHeading

    # called via callback
    def controlEvent(self, key, value, isNew):
        logging.debug("control event received: " + key)
        if key == 'SetTarget':
        	self.control.targeting = value
        elif key == 'IMUHeading':
        	self.control.imuHeading = value
        else:
        	logging.info("Unexpected key in visValueChanged")

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


