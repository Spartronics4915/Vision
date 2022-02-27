#! python3
from subprocess import Popen, PIPE
import win32gui, win32con, time, sys
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
            'active':   'true'
            },
        'back': 
            {
            'name':     "BackCam",
            'coords':   [500, 500],
            'size':     [640, 480],
            'port':     "5807",
            'camip':    "10.49.15.13",
            'user':     "pi",
            'active':   'false'
            },
        'up':
            {
            'name':     "UpCam",
            'coords':   [600, 600],
            'size':     [640, 480],
            'port':     "5806",
            'camip':    "10.49.15.11",
            'user':     "pi",
            'active':   'true'
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

available_actions = ['start', 'stop', 'check']

def startDisplay(display='front', port=None):
    ''' Start a display on a certain port '''
    disp_options = display_info.get(display, None)
    if disp_options:
        disp_port = disp_options.get('port')
    if port:
        disp_port = port
    print("Starting %s display on %s" % (display, disp_port))
    command = "c:\\Users\\spartronics\\StartDisplay.bat"
    p = Popen([command, disp_port])

def moveDisplay(display='front', name=None):
    """ Move and rename a new display window """
    display_spec = display_info.get(display, None)
    if display_spec:
        this_spec = {}
        if name:
            this_spec['name'] = name
        else:
            this_spec['name'] = display_spec.get('name')
        this_spec['coords'] = display_spec.get('coords')
        this_spec['size'] = display_spec.get('size')
        this_spec['old_name'] = 'GStreamer D3D'
        print("Moving display %s to %s" % (this_spec['old_name'], this_spec['name']))
        win32gui.EnumWindows(enumHandlerMove, this_spec)
    else:
        return

def enumHandlerMove(hwnd, lParam):
    old_name = lParam['old_name']
    coords = lParam['coords']
    new_name = lParam['name']
    size = lParam['size']
    if win32gui.IsWindowVisible(hwnd):
        if old_name in win32gui.GetWindowText(hwnd):
            win32gui.MoveWindow(hwnd, 
                    coords[0], coords[1], size[0], size[1], True)
            win32gui.SetWindowText(hwnd,new_name)
            print("Moved window: %s" % hwnd)

def killDisplay(display='front', name=None):
    """ Find and kill an open display """
    display_spec = display_info.get(display, None)
    if display_spec:
        this_spec ={}
        if name:
            this_spec['name'] = name
        else:
            this_spec['name'] = display_spec.get('name')
        print("Killing window with name: %s" % display_spec.get('name'))
        win32gui.EnumWindows(enumHandlerKill, this_spec)
    else:
        return

def enumHandlerKill(hwnd, lParam):
    """ Kill the open window """
    window_name = lParam.get('name')
    if win32gui.IsWindowVisible(hwnd):
        if window_name in win32gui.GetWindowText(hwnd):
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            print("Killed window %s" % hwnd)
        

usage="""
%prog [-h] [options] display start|stop|check"""


def main(argv):
    ''' Main for display start script '''
    parser = OptionParser(usage=usage)
    parser.add_option("-p", type="string", dest="disp_port",
            help="Specify port to listen on")
    parser.add_option("-d", type="string", dest="camera_name",
            help="Specify display to start", default="front")
    parser.add_option("-n", type="string", dest="disp_name",
            help="Specify name for the created display")

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(0)

    # Check that camera is valid
    camera = args[0]
    action = args[1]

    if camera not in available_cameras:
        print("Camera %s is not installed at this time." % camera)
        print("Available cameras are:")
        for item in available_cameras:
            print(item)

    if action not in available_actions:
        print("Invalid action: %s" % action)
        print("Available actions are:")
        for item in available_actions:
            print(item)

    # Set some defaults based on this camera
    camera_def = display_info[camera]

    disp_port = camera_def['port']
    disp_name = camera_def['name']

    # Override if user entered options
    if options.disp_port:
        disp_port = options.disp_port
    if options.disp_name:
        disp_name = options.disp_name

    # the main actions
    if action == 'start':

        startDisplay(display=camera, port=disp_port)
    
        print("Started display")

        time.sleep(5)

        moveDisplay(display=camera, name=disp_name)

    elif action == 'stop':
        killDisplay(display=camera, name=disp_name)


if __name__ == "__main__":
    main(sys.argv[1:])

