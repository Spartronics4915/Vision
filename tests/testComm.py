import comm
import logging
import time

logging.basicConfig(level=logging.DEBUG)

print("starting comm")
c = comm.Comm("localhost") # connect to fake robot on localhost
t = comm.Target()

threshold = time.clock() - .01

while True:
    now = time.clock()
    if now > threshold:
        print(".")
        t.clock = now
        threshold = now + .01 # 100 hz
        if t.angleX == None:
            t.angleX = 0
            t.angleY = 0
        else:
            t.angleX += 1
            t.angleY -= 1
        c.SetTarget(t)
