import comm
import logging
import time

logging.basicConfig(level=logging.DEBUG)

print("starting comm")
c = comm.Comm("localhost") # connect to fake robot on localhost
t = comm.Target()


while True:
    print(".")
    time.sleep(5)
    if t.angleX == None:
        t.angleX = 0
        t.angleY = 0
    else:
        t.angleX += 1
        t.angleY -= 1
    c.SetTarget(t)
