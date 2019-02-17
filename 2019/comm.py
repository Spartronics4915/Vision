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
        We take no opinion on the shape/type of value
        XXX: need a way to represent non-acquisition?
    """
    def __init__(self, v=None, key="Reverse/solvePNP"):
        self.clock = time.clock()
        self.lastclock = self.clock
        self.dashboardKey = key
        self.value = v  # value can be a tuple, a list, a string
        #Invalid, bogus targets, to be changed if something goes ary

    def setValue(self, value, forceupdate=True):
        if forceupdate or value != self.value:
            self.lastclock = self.clock
            self.clock = time.clock()
            self.value = value  # can be a tuple, a list, a string
            return True
        else:
            return False

    def send(self, targetTable):
        # convert the value and the clock to a comma-separated list of numbers
        #  value can be scalar, a tuple or an array, result will be flattened
        #  examples:
        #       value: 1 -> "1,.3566" 
        #       value: (1,2) -> "1,2,.3566" 
        #       value: [1,2,"hello world"] -> "1,2,hello world,.3566" 
        val = []
        try:
            val.extend(self.value) # fails if value is not iterable
        except TypeError:
            val.append(self.value)  # handle the single-number case
        val.append(self.clock - self.lastclock)
        vstr = ",".join(str(x) for x in val)
        #print("send: " + vstr)
<<<<<<< HEAD
        targetTable.putString("solvePNP", vstr)
=======
        targetTable.putString(self.dashboardKey, vstr)
>>>>>>> 58fa510b41a5fb8b64254de3c992e898d7d87dcd

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

            # We communicate target to robot via Vision table,
            # current thinking is that this should not be a subtable of
            # SmartDashboard, since traffic is multiplied by the number
            # of clients.
            self.visionTable = NetworkTables.getTable("/SmartDashboard/Vision/Reverse")
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

    def Shutdown(self):
        NetworkTables.removeConnection(self.connectionListener)
        self.controlTable.removeEntryListener(self.visionControlEvent)

    def SendTarget(self, t):
        self.target = t
        self.target.send(self.visionTable)

    def UpdateTarget(self, value):
        self.target.setValue(value)
        self.target.send(self.visionTable)

    def GetIMUHeading(self):
        return self.control.imuHeading

    def SetFPS(self, fps):
        self.fpsHistory.append(fps)
        self.fpsHistory = self.fpsHistory[-15*4:]
        if time.time() - self.lastUpdate > 5:
            self.target.SetFPS(sum(self.fpsHistory)/len(self.fpsHistory))
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
