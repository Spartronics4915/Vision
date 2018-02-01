import comm
import logging
import time

logging.basicConfig(level=logging.DEBUG)

print("starting comm")
c = comm.Comm("localhost") # connect to fake robot on localhost
t = comm.Target()
updatePeriod = .01 # 100Hz
tickPeriod = 1
nextUpdate = 0
nextTick = 0

time.sleep(2)

while True:
    now = time.clock()
    if now > nextUpdate:
        t.clock = now
        nextUpdate = now + updatePeriod 
        if t.angleX == None:
            t.angleX = 0
            t.angleY = 0
        else:
            t.angleX += 1
            t.angleY -= 1
        c.SetTarget(t)

    if now > nextTick:
        print("<tick>")
        nextTick = now + tickPeriod
