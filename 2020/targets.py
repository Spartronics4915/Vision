#
# manages our characterization of a vision target and its
#   communication via networktables
#

from networktables import NetworkTables
import time
import comm
import logging
import math
import doctest

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
        # Member Varables
        self.subkey = "baseTarget"
        self.autoSend = False
        self.clock = time.monotonic()
        self.value = None

        # Deltaclock computation
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

# Currently no doctests, however if needed un-comment
'''
if __name__ == "__main__":
    # Debug logging
    logFmt = "%(name)-8s %(levelname)-6s %(message)s"
    dateFmt = "%H:%M"
    logging.basicConfig(level=logging.DEBUG,format=logFmt, datefmt=dateFmt)

    logging.info("Began logger")

    doctest.testmod()
'''