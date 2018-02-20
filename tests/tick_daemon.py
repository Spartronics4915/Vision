import time 

starttime = time.time()

with open("home/pi/runPiCam.log", "w") as outputfile:
    outputfile.truncate() #Clear the file

while True:
    time.sleep(1)
    with open("home/pi/runPiCam.log", "w") as outputfile:
        outputfile.write(str(time.time() - starttime) + "\n")
    #  This comment was written in vim and it is super cool
