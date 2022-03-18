#! python3

import sys, socket
from fabric import Connection
from optparse import OptionParser


display_info = {
        'front':
            {
            'name':     "FrontCam",
            'coords':   [400, 400],
            'size':     [640, 480],
            'port':     "5805",
            'camip':    "10.49.15.12",
            'user':     "pi",
            'active':   "true"
            },
        'back':
            {
            'name':     "BackCam",
            'coords':   [500, 500],
            'size':     [640, 480],
            'port':     "5807",
            'camip':    "10.49.15.13",
            'user':     "pi",
            'active':   "false"
            },
        'up':
            {
            'name':     "UpCam",
            'coords':   [600, 600],
            'size':     [640, 480],
            'port':     "5806",
            'camip':    "10.49.15.11",
            'user':     "pi",
            'active':   "true"
            },
        'romi':
            {
            'name':     "Romi",
            'coords':   [600, 600],
            'size':     [640,480],
            'port':     "5820",
            'camip':    "10.0.0.160",
            'user':     "pi",
            'active':   "true"
            }
        }

def get_available_cameras():
    """ Check display_info list for active cameras """
    active = []
    for camera in display_info.keys():
        camera_info = display_info[camera]
        is_active = camera_info['active']
        if is_active == 'true':
            active.append(camera)
    return active

available_cameras = get_available_cameras()
available_actions = ["start", "stop", "check"]

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.49.15.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def startCamera(port='5805', camera_ip='10.49.15.12', user='pi'):
    """ Start a camera process on a Raspberry Pi camera """
    my_ip = get_ip()
    command = "./gstreamit.sh %s %s > /dev/null 2>&1 &" % (my_ip, port)
    result = Connection(camera_ip,user=user).run(command, hide=True)
    msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
    print(msg.format(result))

def killCamera(camera_ip='10.49.15.12', user='pi'):
    """ Kill the camera process """
    command = "./kill_gstream.sh > /dev/null 2>&1 &"
    result = Connection(camera_ip,user=user).run(command, hide=True)
    msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
    print(msg.format(result))

def checkCamera(camera_ip='10.49.15.12', user='pi', name='FrontCam'):
    """ Check the camera process """
    command = "./check_gstream.sh"
    result = Connection(camera_ip,user=user).run(command, hide=True)
    msg = "{0.stdout}"
    print("%s: " % name)
    print(msg.format(result))


usage="""
%prog [-h] [options] front|back|up|all start|stop|check"""


def main(argv):


    parser = OptionParser(usage=usage)
    parser.add_option('-p', dest='port_override', type='string',
            help='Override the default port for video for selected camera')
    parser.add_option('-a', dest='addr_override', type='string',
            help='Override the default IP address for the selected camera')
    parser.add_option('-u', dest='user_override', type='string',
            help='Override the default user for the selected camera')

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(0)


    # Check that camera is valid
    camera = args[0].lower()
    action = args[1].lower()

    # Check that the right static IP has been set
    my_ip = get_ip()
    if camera != "romi" and "49.15" not in my_ip:
        print("********************************************************************")
        print("      Incorrect ip: %s" % my_ip)
        print("      Make sure you set up the Wi-Fi connection!!!")
        print("********************************************************************")

        input("Enter any key")
        sys.exit()

    cameras = []
    if camera == 'all':
        cameras = available_cameras
    else:
        cameras.append(camera)

    if camera != 'all' and camera not in available_cameras:
        print("Camera %s is not installed at this time." % camera)
        print("Available cameras are:")
        for item in available_cameras:
            print(item)

    if action not in available_actions:
        print("Invalid action: %s" % action)
        print("Available actions are:")
        for item in available_actions:
            print(item)

    # Now loop through camera list
    for camera in cameras:

        # Set some defaults based on this camera
        camera_def = display_info[camera]
    
        cam_port = camera_def.get('port')
        cam_ip = camera_def.get('camip')
        cam_user = camera_def.get('user')
        cam_name = camera_def.get('name')
    
        # Override if user entered options
        if options.port_override:
            cam_port = options.port_override
        if options.addr_override:
            cam_ip = options.addr_override
        if options.user_override:
            cam_user = options.user_override

        if action == 'start':

            startCamera(port=cam_port, camera_ip=cam_ip, user=cam_user)

        elif action == 'stop':
    
            killCamera(camera_ip=cam_ip, user=cam_user)

        elif action == 'check':

            checkCamera(camera_ip=cam_ip, user=cam_user, name=cam_name)


if __name__ == "__main__":
    main(sys.argv[1:])

