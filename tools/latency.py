#!/usr/bin/python3
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")
import argparse, time
from networktables import NetworkTables

import logging
logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description="Test roundtrip latency between a NetworkTables server and client.")
parser.add_argument("--client", action="store_true", help="run in client mode")
parser.add_argument("--server", action="store_true", help="run in server mode")
parser.add_argument("--host", action="store_true", default="127.0.0.1")
parser.add_argument("--port", type=int, default="1735")
args = parser.parse_args()

last_time = time.perf_counter()

def clientValueChanged(table, key, value, isNew):
    global last_time
    if key != "latency" or value != "server":
        return
    print(str((time.perf_counter()-last_time)/1000) + "ms")
    last_time = time.perf_counter()
    sd.putString("latency", "client")

def serverValueChanged(table, key, value, isNew):
    global last_time
    if key != "latency" or value != "client":
        return
    sd.putString("latency", "server")

if args.server:
    sd = NetworkTables.getTable("SmartDashboard")
    last_time = time.perf_counter()
    sd.putString("latency", "server")
    sd.addTableListener(serverValueChanged)
else:
    NetworkTables.initialize(server=args.host) # This only wants to host, not the port
    sd = NetworkTables.getTable("SmartDashboard")
    sd.putString("latency", "client")
    sd.addTableListener(clientValueChanged)

NetworkTables.ipAddress = args.host
NetworkTables.port = args.port

while True:
    time.sleep(1)
