#!/usr/bin/python3

import sys
import os

print("Utility to switch between rw or ro filesystem for WPI rasberry pi image")

while(True):
    wanted_state = input("Which filesystem would you like? ro/rw \n")

    if wanted_state == 'ro':
        #print('ro')
        os.system('/bin/mount -o remount,ro / && /bin/mount -o remount,ro /boot')
        break
    elif wanted_state == 'rw':
        #print('rw')
        os.system('/bin/mount -o remount,rw / && /bin/mount -o remount,rw /boot')
        break
    else:
        print('Not a valid option')
