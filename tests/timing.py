#!/usr/bin/env python

'''
This module contains minimal support for timing things..
'''

import cv2
from contextlib import contextmanager

def clock():
    return cv2.getTickCount() / cv2.getTickFrequency()

@contextmanager
def Timer(msg):
    print msg, '...',
    start = clock()
    try:
        yield
    finally:
        print "%.2f ms" % ((clock()-start)*1000)

class StatValue:
    def __init__(self, smooth_coef = 0.5):
        self.value = None
        self.history = [0, 0]
        self.ih = 0
        self.c = smooth_coef
        self.invc = 1.0 - smooth_coef

    def update(self, v):
        self.history[self.ih] = v
        self.ih = (self.ih + 1) % 2
        if self.value == None:
            self.value = v
        else:
            self.value = self.history[self.ih]*self.invc + v*self.c

