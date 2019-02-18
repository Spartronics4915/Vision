#
#   manages our characterization of a vision target and its
#   communication via networktables
#

from networktables import NetworkTables
import time
import comm
import logging

class Target:
    """
        Target represents the data vision passes to robot.
        We take no opinion on the shape/type of value
        XXX: need a way to represent non-acquisition?
        Subclasses should override send to convert the incoming
        value to an alternate representation.

        Vision/Target  number;dtime
    """
    def __init__(self):
        self.visionTable = comm.GetVisionTable()
        self.vistabKey = "Target"
        self.autoSend = False
        self.clock = time.monotonic()
        self.lastclock = 0
        self.deltaclock = 0
        self.value = None

    def setValue(self, value, forceupdate=True):
        if forceupdate or value != self.value:
            self.lastclock = self.clock
            self.clock = time.monotonic()
            self.deltaclock = self.clock - self.lastclock
            self.value = value  # expect a tuple or list
            if self.autoSend:
                self.send()
            return True
        else:
            return False

    # override me to present alternate respresentation
    def send(self):
        self.visionTable.putString(self.vistabKey,
                "{0};{1}".format(str(self.value), str(self.deltaclock)))

class TargetPNP(Target):
    """
    TargetPNP:
        Vision/Reverse/solvePNP [dxL,dyL,dthetaL,dxR,dyR,dthetaR,dtime]
                                [dxL,dyL,dthetaL,dtime]
    """
    def __init__(self, left, right, orientation="Reverse"):
        super().__init__()
        self.vistabKey = orientation+"/solvePNP"
        self.leftTarget = left
        self.rightTarget = right

    # here: value is presumed to be a tuple of length 2
    def setValue(self, value, forceupdate=True):
        if len(value) == 1:
            self.leftTarget = value
            self.rightTarget = None
        elif len(value) == 2:
            self.leftTarget,self.rightTarget = value
        else:
            logging.error("TargetPNP: invalid setValue")
        super().setValue(value, forceupdate)

    def send(self):
        # solvePNP convention for target:
        #     all numbers, 3 per target, 1 timestamp
        arrayValue = []
        if self.leftTarget != None:
            arrayValue.extend(self.leftTarget)
        if self.rightTarget != None:
            arrayValue.extend(self.rightTarget)
        arrayValue.append(self.deltaclock)
        # logging.info("send: " + str(arrayValue))
        self.visionTable.putNumberArray(self.vistabKey, arrayValue)
