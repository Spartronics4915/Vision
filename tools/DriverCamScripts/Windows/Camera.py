#! python3

import sys
from socket import getaddrinfo, gethostname
import ipaddress
from optparse import OptionParser
from fabric import Connection
# we use Connection to launch the gstreamer remotely on the raspberry pi over SSH
# to do this we cannot use the default SSH port 22 as it's blocked by firewall on the FMS
# So we will depend on seting up sshd on the pi to use port 5801 instead

display_info = {
        'driver':
            {
            'name':     "DriverCam",
            'coords':   [1265, 0],
            'size':     [640, 480],
            'port':     "5805",
            'camip':    "10.49.15.12",
            'user':     "pi",
            'ssh':      "5801",
            'active':   'true'
            },
        'front':
            {
            'name':     "FrontCam",
            'coords':   [400, 400],
            'size':     [640, 480],
            'port':     "5805",
            'camip':    "10.49.15.11",
            'user':     "pi",
            'ssh':      "5801",
            'active':   'false'
            },
        'back':
            {
            'name':     "BackCam",
            'coords':   [500, 500],
            'size':     [640, 480],
            'port':     "5807",
            'camip':    "10.49.15.13",
            'user':     "pi",
            'ssh':      "5801",
            'active':   'true'
            },
        'up':
            {
            'name':     "UpCam",
            'coords':   [600, 600],
            'size':     [640, 480],
            'port':     "5806",
            'camip':    "10.49.15.14",
            'user':     "pi",
            'ssh':      "5801",
            'active':   'false'
            },
        'romi':
            {
            'name':     "Romi",
            'coords':   [600, 600],
            'size':     [640, 480],
            'port':     "5808",
            'camip':    "10.49.15.15",
            'user':     "pi",
            'ssh':      "5801",
            'active':   'false'
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

def get_all_ips(ip_addr_proto="ipv4", ignore_local_ips=True):
    # By default, this method only returns non-local IPv4 addresses
    # To return IPv6 only, call get_ip('ipv6')
    # To return both IPv4 and IPv6, call get_ip('both')
    # To return local IPs, call get_ip(None, False)
    # Can combine options like so get_ip('both', False)

    af_inet = 2
    if ip_addr_proto == "ipv6":
        af_inet = 30
    elif ip_addr_proto == "both":
        af_inet = 0

    system_ip_list = getaddrinfo(gethostname(), None, af_inet, 1, 0)
    ip_list = []

    for ip in system_ip_list:
        ip = ip[4][0]

        try:
            ipaddress.ip_address(str(ip))
            ip_address_valid = True
        except ValueError:
            ip_address_valid = False
        else:
            if ipaddress.ip_address(ip).is_loopback and ignore_local_ips or ipaddress.ip_address(ip).is_link_local and ignore_local_ips:
                pass
            elif ip_address_valid:
                ip_list.append(ip)

    return ip_list

def get_ip():
    ip_list = get_all_ips()

    for ipaddr in ip_list:
        if '10.49.15' in ipaddr:
            return ipaddr
    return None

def startCamera(port='5805', camera_ip='10.49.15.12', user='pi', ssh='5801'):
    """ Start a camera process on a Raspberry Pi camera """
    my_ip = get_ip()
    command = "./gstreamit.sh %s %s > /dev/null 2>&1 &" % (my_ip, port)
    result = Connection(camera_ip,user=user,port=ssh).run(command, hide=False)
    msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
    print(msg.format(result))

def killCamera(camera_ip='10.49.15.12', user='pi', ssh='5801'):
    """ Kill the camera process """
    command = "./kill_gstream.sh > /dev/null 2>&1 &"
    result = Connection(camera_ip,user=user,port=ssh).run(command, hide=False)
    msg = "Ran {0.command!r} on {0.connection.host}, got stdout:\n{0.stdout}"
    print(msg.format(result))

def checkCamera(camera_ip='10.49.15.12', user='pi', name='FrontCam', ssh='5801'):
    """ Check the camera process """
    is_running = False
    command = "./check_gstream.sh"
    result = Connection(camera_ip,user=user,port=ssh).run(command, hide=False)
    msg = "{0.stdout}"
    print("%s: " % name)
    print(msg.format(result))
    if result == "Running":
        is_running = True
    return is_running


usage="""
%prog [-h] [options] driver|front|back|up|all start|stop|check"""


def main(argv):


    # Check that the right static IP has been set
    my_ip = get_ip()
    if  not my_ip:
        print("********************************************************************")
        print("      Incorrect ip: %s" % my_ip)
        print("      Make sure you set up the Wi-Fi connection!!!")
        print("********************************************************************")

        input("Enter any key")
        sys.exit()

    parser = OptionParser(usage=usage)
    parser.add_option('-p', dest='port_override', type='string',
            help='Override the default port for video for selected camera')
    parser.add_option('-a', dest='addr_override', type='string',
            help='Override the default IP address for the selected camera')
    parser.add_option('-u', dest='user_override', type='string',
            help='Override the default user for the selected camera')
    parser.add_option('-s', dest='ssh_override', type='string',
            help='Override the default SSH port for the selected camera')

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(0)


    # Check that camera is valid
    camera = args[0].lower()
    action = args[1].lower()

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
        cam_ssh = camera_def.get('ssh')
    
        # Override if user entered options
        if options.port_override:
            cam_port = options.port_override
        if options.addr_override:
            cam_ip = options.addr_override
        if options.user_override:
            cam_user = options.user_override
        if options.ssh_override:
            cam_ssh = options.ssh_override

        if action == 'start':

            startCamera(port=cam_port, camera_ip=cam_ip, user=cam_user, ssh=cam_ssh)

        elif action == 'stop':
    
            killCamera(camera_ip=cam_ip, user=cam_user, ssh=cam_ssh)

        elif action == 'check':

            checkCamera(camera_ip=cam_ip, user=cam_user, name=cam_name, ssh=cam_ssh)


if __name__ == "__main__":
    main(sys.argv[1:])

