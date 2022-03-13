#! python3
from subprocess import Popen, PIPE
import win32gui, win32con, time, sys, socket
from optparse import OptionParser

# Messy
global WindowPos


display_info = {
        'front': 
            {
            'name':     "FrontCam",
            'coords':   [1265, 0],
            'coords2':   [1937, 10],
            'coords3':   [1928, 10],
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
            'coords2':   [500, 500],
            'coords3':   [500, 500],
            'size':     [640, 480],
            'port':     "5807",
            'camip':    "10.49.15.13",
            'user':     "pi",
            'active':   'false'
            },
        'up':
            {
            'name':     "UpCam",
            'coords':   [1265, 472],
            'coords2':   [2565, 10],
            'coords3':   [1928, 485],
            'size':     [640, 480],
            'port':     "5806",
            'camip':    "10.49.15.11",
            'user':     "pi",
            'active':   'true'
            }
        }

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

available_actions = ['start', 'stop', 'check', 'find', 'portrait', 'landscape']

def startDisplay(display='front', port=None):
    ''' Start a display on a certain port '''
    global WindowPos
    disp_options = display_info.get(display, None)
    if disp_options:
        disp_port = disp_options.get('port')
    if port:
        disp_port = port
    print("Starting %s display on %s" % (display, disp_port))
    command = "c:\\Users\\spartronics\\StartDisplay.bat"
    WindowPos = False
    p = Popen([command, disp_port])

def moveDisplay(display='front', name=None, orientation=None):
    """ Move and rename a new display window """
    display_spec = display_info.get(display, None)
    if display_spec:
        this_spec = {}
        if name:
            this_spec['name'] = name
        else:
            this_spec['name'] = display_spec.get('name')
        if orientation == 'landscape':
            this_spec['coords'] = display_spec.get('coords2')
        elif orientation == 'portrait':
            this_spec['coords'] = display_spec.get('coords3')
        else:
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

def checkDisplay(display='front', name=None):
    """ Check to see if display is running """
    display_spec = display_info.get(display, None)

    if display_spec:
        this_spec = {}
        if name:
            this_spec['name'] = name
        else:
            this_spec['name'] = display_spec.get('name')
        win32gui.EnumWindows(enumHandlerCheck, this_spec)

def enumHandlerCheck(hwnd, lParam):
    """ Is window open? """
    window_name = lParam.get('name')
    if win32gui.IsWindowVisible(hwnd):
        if window_name in win32gui.GetWindowText(hwnd):
            print("%s found: %s" % (window_name, hwnd))

def findDisplay(display='front', name=None):
    """ Move and rename a new display window """
    global WindowPos
    display_spec = display_info.get(display, None)
    if display_spec:
        this_spec = {}
        if name:
            this_spec['name'] = name
        else:
            this_spec['name'] = display_spec.get('name')
        print("Find: %s" % this_spec['name'])
        WindowPos = False
        win32gui.EnumWindows(enumHandlerFind, this_spec)

def enumHandlerFind(hwnd, lParam):
    name = lParam['name']
    global WindowPos
    if win32gui.IsWindowVisible(hwnd):
        if name in win32gui.GetWindowText(hwnd):
              rect = win32gui.GetWindowRect(hwnd)
              x = rect[0]
              y = rect[1]
              w = rect[2] - x
              h = rect[3] - y
              print("%s window info: %s, %s, %s, %s"% (name, x, y, w, h))
              WindowPos = True

usage="""
%prog [-h] [options] display|all start|stop|check"""


def main(argv):
    global WindowPos
    WindowPos = False

    # Check to see if correct IP has been set
    my_ip = get_ip()
    if "49.15" not in my_ip:
        print("********************************************************************")
        print("      Incorrect ip: %s" % my_ip)
        print("      Make sure you set up the Wi-Fi connection!!!")
        print("********************************************************************")

        input("Enter any key")
        sys.exit()

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
    camera = args[0].lower()
    action = args[1].lower()

    displays = []
    if camera == 'all':
        displays = available_cameras
    else:
        displays.append(camera)

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
    for camera in displays:

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

            #time.sleep(5)
            for x in range(5):
                findDisplay(display=camera, name=disp_name)
                if WindowPos:
                    break

                moveDisplay(display=camera, name=disp_name)
                time.sleep(2)

        elif action == 'landscape':

            startDisplay(display=camera, port=disp_port)
    
            print("Started display")

            #time.sleep(5)
            for x in range(5):
                findDisplay(display=camera, name=disp_name)
                if WindowPos:
                    break

                moveDisplay(display=camera, name=disp_name, orientation='landscape')
                time.sleep(2)

        elif action == 'portrait':

            startDisplay(display=camera, port=disp_port)
    
            print("Started display")

            #time.sleep(5)
            for x in range(5):
                findDisplay(display=camera, name=disp_name)
                if WindowPos:
                    break

                moveDisplay(display=camera, name=disp_name, orientation='portrait')
                time.sleep(2)

        elif action == 'stop':

            killDisplay(display=camera, name=disp_name)

        elif action == 'check':

            checkDisplay(display=camera, name=disp_name)

        elif action == 'find':
            findDisplay(display=camera, name=disp_name)

        # Wait a little bit
        #time.sleep(3)


if __name__ == "__main__":
    main(sys.argv[1:])

