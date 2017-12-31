import comm
import logging
import time

logging.basicConfig(level=logging.DEBUG)

print("starting comm")
c = comm.Comm("localhost") # connect to fake robot on localhost


while True:
    print(".")
    time.sleep(5)
