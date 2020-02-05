import cv2
import numpy as np
from networktables import NetworkTables
import ..mathutils.transformations

def updateRobotState(table, key, value, isNew):

def updateLauncherState(table, key, value, isNew):

def main():
    videostream = cv2.VideoCapture(0)

    # we're a client of the robot
    NetworkTables.initialize(server="localhost")
    self.robotStateTable = NetworkTables.getTable("/SmartDashboard/RobotState")
    self.robotStateTable = NetworkTables.addEntryListener(updateRobotState)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Display the resulting frame
        cv2.imshow('frame', frame)

        # here's where process the frame
        #
        # (success, rotVec, xlatVec) = cv2.solvePnP(...)
        #
        rotVec = np.array([1,2,])
        (rotmat, _) = cv2.Rodrigues(rotVec)

        # after processing the frame we convert our result into
        # a form that the robot code can use

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()
