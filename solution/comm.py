#
# comm:
#   manages our connection to the robot
#

from networktables import NetworkTables
import sys, traceback, time
import json
import logging

class Control:
    """
        Control signals are sent by robot or driver station,
        Received by vision processor to guide its behavior.
    """
    def __init__(self):
        self.targeting = None
        self.imuHeading = None

class Target:
    """
        Target represents the data vision passes to robot.
        XXX: need a way to represent non-acquisition?
    """
    def __init__(self):
        self.clock = time.clock()
        self.angleX = 0
        self.angleY = 0

    def Send(self, targetTable):
        targetTable.putNumber("clock", self.clock)
        targetTable.putNumber("ax", self.angleX)
        targetTable.putNumber("ay", self.angleY)

theComm = None

class Comm:
    """
        Comm abstracts our network-tables conventions.
        Can be instantiated either by the vision processor or
        by the fake robot server.  
    """
    def __init__(self, serverIP):
        try:
            # IPAddress can be 
            #   - None: means run as fake server
            #   - ip: "10.49.15.2" or 
            #   - name: "roboRIO-4915-FRC", "localhost"
            if serverIP != None:
                # we're a client
                self.asServer = False
                NetworkTables.initialize(server=serverIP)
                NetworkTables.setUpdateRate(.01)  
                # default is .05 (50ms/20Hz), .01 (10ms/100Hz)
            else:
                # we're fake server
                self.asServer = True
                NetworkTables.initialize() 

            theComm = self # for callback access

            # update the dashboard with our state, NB: this is a different table
            # that both the vision and control tables.
            self.sd = NetworkTables.getTable("SmartDashboard")
            self.sd.putString("Vision/Status", "OK")
            self.updateVisionState("Standby")
            
            # We communcate target to robot via Vision table,
            # current thinking is that this should not be a subtable of
            # SmartDashboard, since traffic is multiplied by the number
            # of clients.
            self.visionTable = NetworkTables.getTable("Vision")
            self.controlTable = NetworkTables.getTable("VisionControl")

            self.control = Control()
            self.target = Target()

            self.fpsHistory = []
            self.lastUpdate = time.time()
            
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
            print("ERROR initializing network tables", xcpt[0])
            traceback.print_tb(xcpt[2])

    def updateVisionState(self, state):
        self.sd.putString("Vision/State", state)

    def GetVisionTable(self):
        return self.visionTable

    def GetVisionControlTable(self):
        return self.controlTable

    def Shutdown(self):
        NetworkTables.removeConnection(self.connectionListener)
        self.controlTable.removeEntryListener(self.visionControlEvent)

    def SetTarget(self, t):
        self.target = t
        self.target.Send(self.visionTable)

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
        print("control event received: " + key)
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
