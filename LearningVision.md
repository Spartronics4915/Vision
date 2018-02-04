### What camera are we using and why?
> The decided solution is the PiCam for the rasberry pi. There are muliple advantages that the PiCam gives us, compared to the standard USB Microsoft Livecam 3000 HD. From Adafruit "This interface uses the dedicated CSI interface, which was designed especially for interfacing to cameras. The CSI bus is capable of extremely high data rates, and it exclusively carries pixel data." Giving us the upper hand in terms of data transmission, and communication protocals.

> In addition, the Picam is completly customizeable from the box. Using 'raspivid -d' command, you can see a demo of all the different setting and features the picam has to offer. In our case, we have elected to settle on a brigness setting of 70, and a contrast setting of 70. Obdisouly the objective with these settings is to isloate the high saturation of the cube, such that when we send it over to the pipeline, there is very little computation having to be done on that end.

### How is this repository organised?
> The vision repository is seprate from the other annual repositories because much of the code and process does not change with the game, rather the code and process only change if we decide to implement a different vision solution, or new versions of libraries are released.

> In terms of directories and folders, this repository is quite straightforward. The 'tools' directory is used to contain the scripts that will be used to tune varies objects, such as the camera itself, or find what filters and blurs are going to be effective for that years game.

> The tests folder contains much more concrete programs compared to the tools directory. In the tests diretory there is many simple scrips that just display an image, for the purpace of testing weather those respective devices are in operation or not. It also contains some scrips to test 'pynetworktables', as well as tune the picam (Arguably belongs in the tools directory).

> Finally, the solution directoy is fairly self-explaitory. The scrips 'algo', 'comm', and 'picam' are all libraries, being used in the 'runPiCam' script to bring it all together. Also in that directory you can find a mjpeg streamer script, which we have integrated with our SmartDashboard to display the picam's view, to the drivers.
