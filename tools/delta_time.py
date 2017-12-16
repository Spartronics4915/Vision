#!/usr/bin/python2
import argparse, time
from networktables import NetworkTables

import logging
logging.basicConfig(level=logging.DEBUG) # so we can see NetworkTables log messages

SECONDS_TO_MILLISECONDS = 1e5 # it appears that one time.clock() second is 0.01

parser = argparse.ArgumentParser(description="Display the delta time between the last two changes to NetworkTables. This is designed to run as a server, but a simple client is provided for convinience when testing.")
parser.add_argument("--client", action="store_true", help="run in client mode")
parser.add_argument("--host", help="hostname/ip to listen on (or, in client mode, to connect to)", default="127.0.0.1")
parser.add_argument("--port", type=int, help="port to connect to or listen on", default="1735")
parser.add_argument("--update-delay", type=float, dest="delay", help="delay in seconds between each iteration of the update loop (this only really matters in client mode, although it affects both modes)", default="1.0")
args = parser.parse_args()

NetworkTables.ipAddress = args.host
NetworkTables.port = args.port

lastTime = 0

def serverValueChanged(table, key, value, isNew):
    global lastTime
    print((time.clock()-lastTime)*SECONDS_TO_MILLISECONDS, "milliseconds of delta time.")
    lastTime = time.clock()

if args.client:
    NetworkTables.initialize(server=args.host)
    sd = NetworkTables.getTable("SmartDashboard")
else:
    sd = NetworkTables.getTable("SmartDashboard")
    sd.addTableListener(serverValueChanged)

while True:
    time.sleep(args.delay)
    if args.client:
        sd.putNumber("foo", time.clock())
        
