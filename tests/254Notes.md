## Notes on Team 254 FRC-2017 codebase

#### Robot
* has-a RobotState
* has-a VisionServer
* has-a Looper (mEnabledLooper)
    * enables VisionProcessor singleton
    * enables RobotStateEstimator singleton

#### VisionServer
* is-a CrashTrackingRunnable
* has-a list of VisionUpdateReceivers
* has-a ServerThread (actually a list, but..)


#### VisionServer::ServerThread
* is-a CrashTrackingRunnable   (Runnable implements run())
* implements handleMessage, called via runCrashTracxked()
    * timestamps messages when they are received (over the wire)
    * produces a VisionUpdate object which is distributed to all receivers
* has-a VisionServer::AppMaintenanceThread to keep adb in healthy state

#### VisionProcessor
* is-a singleton
* is-a Loop (-> onLoop, etc)
* is-a VisionUpdateReceiver (->gotUpdate)
* registered with mEnabledLooper
* onLoop:  invokes robotState->addVisionUpdate(VisionUpdate)

#### VisionUpdate
* parses json string from droidphone
* has-a capturedAgoMs
* has-a capturedAtTimestamp - (presumes no comm latency)
* has-a TargetInfo[]

#### TargetInfo
* has-a x, y, z (represents location in space)

#### RobotStateEstimator
* is-a singleton
* is-a Loop (-> onLoop)
    * samples drive encoders (left/right)
    * samples gyro
    * sampledV = generateOdometryFromSensors(deltaLeft/Right, gyro)
    * predictedV = Kinematics.fwd(leftV, rightV)
    * -> addObservations(sampledV, predictedV)

#### RobotState
keeps track of the poses of various coordinate frames throughout
the match. A coordinate frame is simply a point and direction in space that
defines an (x,y) coordinate system. Transforms (or poses) keep track of the
spatial relationship between different frames.

Robot frames of interest (from parent to child):
* Field frame: origin is where the robot is turned on
* Vehicle frame: origin is the center of the robot wheelbase, facing fwd
* Camera frame: origin is the center of the camera imager relative to
  the robot base.
* Goal frame: origin is the center of the boiler (note that orientation
  in this frame is arbitrary). Also note that there can be multiple goal
  frames.
As a kinematic chain with 4 frames, there are 3 transforms of interest:
* Field-to-vehicle: This is tracked over time by integrating encoder and
  gyro measurements. It will inevitably drift, but is usually accurate
  over short time periods.
* Vehicle-to-camera: This is a constant.
* Camera-to-goal: This is a pure translation, and is measured by the vision
  system.

RobotState class definition
* is-a singleton
* maintains list of 100 most recent observations
* has-a GoalTracker
* has-a InterpolatingTreeMap<time, transform> field_to_vehicle;
* implements addObservations(timestamp, measured_V, predicted_V);
    * addFieldToVehicleObs(timestamp, Kinematics.integFwd(mv,pV)
* implements getFieldToVehicle(timestamp)
    * interpolates the field
* implements getFieldToCaemra(timestamp)
    *
* implements addVisionUpdate(TargetInfo[])
    * corrects for camera pitch and yaw as installed on robot
    * estimates distance to Boiler via known height to target
    * transforms from field_to_camera to field_to_goals
    * invokes goalTracker.update(

#### RigidTransform2d
* has-a Translate2d
* has-a Rotation2d

#### Drive
* is-a Subsystem
* has-a DriveControlState (enumerating all possible drive states)
    (OPEN_LOOP, VELOCITY_SETPOINT, PATH_FOLLOWING, AIM_TO_GOAL, etc)
* has-a PathFollower
* has-a Loop subclass, delivered via registerEnabledLoops
    * implements onLoop which behaves according to mDriveControllerState
        * PATH_FOLLOWING: ->updatePathFollower
* implements updatePathFollower:
    * getCurrentPose(), 
    * Twist2d cmd = mPathFollower.update(), 
    * if(!done) updateVelocitySetpoint(Kinematics.inverseKinematics(cmd))

#### PathFollower
* has-a Path
* has-a AdaptivePurePursuitController: mSteeringController
* has-a ProfileFollower: mVelocityController
* implements update():
    * mSteeringController->update() returns APPC::Command
    * mVelocityController.setGoalAndConstraints

## Notes on 254 Vision_app

#### CameraTargetInfo
* has a m_y, m_z (x is "optical axis", y is left/right, z is top/bottom)
  (m_x is always 1, so distance detection occurs on client)


