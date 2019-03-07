#
#   manages our characterization of a vision target and its
#   communication via networktables
#

from networktables import NetworkTables
import time
import comm
import logging
import math

class Target:
    """
        Target represents the data vision passes to robot.
        We take no opinion on the shape/type of value
        XXX: need a way to represent non-acquisition?
        Subclasses should override send to convert the incoming
        value to an alternate representation.

        Vision/Target  number;dtime
    """
    lastUpdate = 0  # Nb: class variable, shared across instances

    def __init__(self, updateDelta=True):
        self.subkey = "Target"
        self.autoSend = False
        self.clock = time.monotonic()
        self.value = None
        if updateDelta:
            # Used when setValue *is* construction, NB: if there
            # are > 1 live targets in the codebase, this isn't
            # valid.
            self.deltaclock = self.clock - Target.lastUpdate
            Target.lastUpdate = self.clock
        else:
            self.deltaclock = 0
            self.lastUpdate = self.clock

    def setValue(self, value, forceupdate=True):
        if forceupdate or value != self.value:
            self.clock = time.monotonic()
            self.deltaclock = self.clock - self.lastUpdate
            self.lastUpdate = self.clock
            self.value = value  # expect a tuple or list
            if self.autoSend:
                self.send()
            return True
        else:
            return False

    # override me to present alternate respresentation
    def send(self):
        comm.PutString(self.subkey,
                "{0};{1}".format(str(self.value), str(self.deltaclock)))

class TargetPNP(Target):
    """
    TargetPNP:
        Vision/Reverse/solvePNP [dxL,dyL,dthetaL,dxR,dyR,dthetaR,dtime]
                                [dxL,dyL,dthetaL,dtime]
    """
    def __init__(self, left, right, orientation="Reverse"):
        super().__init__()
        self.subkey = orientation+"/solvePNP"
        self.leftTarget = left
        self.rightTarget = right

    def __str__(self):
        arrayValue = []
        if self.leftTarget != None:
            arrayValue.extend(self.leftTarget)
        if self.rightTarget != None:
            arrayValue.extend(self.rightTarget)
        if len(arrayValue) == 3:
            arrayValue[2] = math.degrees(arrayValue[2])
        elif len(arrayValue) == 6:
            arrayValue[2] = math.degrees(arrayValue[2])
            arrayValue[5] = math.degrees(arrayValue[5])
        arrayValue.append(int(1000*self.deltaclock))
        return "TargetPNP: " + ("{:.2f}, "*len(arrayValue)).format(*arrayValue)

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
        comm.PutNumberArray(self.subkey, arrayValue)

class TargetHeadingsAndHeightOffset(Target):

    def __init__(self,headings,hError, orientation="Reverse"):
        super().__init__()
        self.subkey = orientation+"/heading"
        self.headings = headings
        self.hError = hError

    def __str__(self):
        arrayValue = []
        arrayValue.extend(self.headings)
        arrayValue.extend(self.hError)
        arrayValue.append(int(1000*self.deltaclock))
        return "Headings-n-Heights: " + ("{:.2f}, "*len(arrayValue)).format(*arrayValue) 

    # Currently no override to the super.setValue()

    def send(self):
        # TargetHeadings convention for target:
        #     all numbers, 2 per target, 1 timestamp
        arrayValue = []
        arrayValue.extend(self.headings)
        arrayValue.extend(self.hError)
        arrayValue.append(self.deltaclock)
        # logging.info("send: " + str(arrayValue))
        comm.PutNumberArray(self.subkey, arrayValue)



    
