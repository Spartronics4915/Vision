## Applications

* `runPiCam.py` - primary entrypoint when running in competition 
  (no server currently).  To get the highest framerate, we run 
  the frame-capture in a separate thread from the algorithm.

## Library

* `algo.py` - collection of various vision pipelines
* `picam.py` - thin vaneer atop PiCamera, support for threaded streaming
* `comm.py` - manage communication with robot via networktables
* `targets.py` - abstraction for target nettab representation

## Difference from 2019

<<<<<<< HEAD
* *Config Changes* - Config objects have been more forcefully implemented in `algo.py`, the objective moving forward is to have more and more data accessible through config objects.
* *Debug Messages* - The precise way debugging is going to be implemented is still in limbo.
=======
* *Config Changes* - Config objects have been more forcefully implemented in `algo.py`, the objective moving forward is to have more and more data accessible through config objects. Algo is selected through config, and 
* *Debug Messages* - The precise way debugging is going to be used is still in limbo.
>>>>>>> daebbf1a905b6ac8ca78aa0194e97e908ae77fd0
* *Lack of 2019-specific code* - `targets.py`, `algo.py`, `rectUtil.py`, `poseEstimation.py`, and `config.py` have all been stripped of 2019-specfici code. In some cases that means removing the files, in others it means simply cutting chunks. Untill kickoff, this directory is designed to be a blank slate, improving on infrastructure from 2019.
* *Planned Threading Changes* - Theading is planned to play a larger role in this version of the codebase. Stay tuned.
* *Parsed Agument Changes* - Parsed arguments are now more tightly entertwined with configurations. When arguments are parsed the chosen `config` is updated with the parsed values. Parsed arguments supeceed `config` values. 
