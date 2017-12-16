#!/usr/bin/python3
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")
import argparse, time, numpy as np
from networktables import NetworkTables

import logging
logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description="Test roundtrip latency between a NetworkTables server and client.")
parser.add_argument("--server", action="store_true", help="run in server mode")
parser.add_argument("--host", help="hostname to connect to or listen on", default="127.0.0.1")
parser.add_argument("--port", type=int, help="port to connect to or listen on", default="1735")
parser.add_argument("--samples", type=int, dest="total_samples", help="number of roundtrip latency samples to average", default="100")
args = parser.parse_args()

if args.server:
    sd = NetworkTables.getTable("SmartDashboard")
    last_time = time.perf_counter()
    sd.putString("latency", "server")
else:
    NetworkTables.initialize(server=args.host) # This only wants the host/ip, not the port
    sd = NetworkTables.getTable("SmartDashboard")
    sd.putString("latency", "client")

NetworkTables.ipAddress = args.host
NetworkTables.port = args.port

sample_index = 0
if not args.server: # We don't need to allocate this memory if we're a server
    samples = np.zeros(args.total_samples)
    last_time = time.perf_counter()

while sample_index < args.total_samples:
    # This loop thrashes the CPU when we're connected, but it's the only way to
    # get accurate readings. The limited samples are implemented so this doesn't
    # run for too long, and because we only really need limited samples.
    if not NetworkTables.isConnected():
        time.sleep(1)
        if args.server:
            continue
        else:
            print("Couldn't connect to a NetworkTables server on",args.host+":"+str(args.port))
            continue

    value = sd.getString("latency")
    if value == "server" and not args.server:
        # We multiply by 1000 to convert from seconds to milleseconds
        samples[sample_index] = (time.perf_counter()-last_time)*1000
        last_time = time.perf_counter()
        sd.putString("latency", "client")
        sample_index += 1
    elif value == "client" and args.server:
        sd.putString("latency", "server")

np.delete(samples, 0) # The first element is garbage because we have to wait for a connection
print("Average roundtrip latency:", np.average(samples), "milleseconds.")
