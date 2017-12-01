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
        self.smooth_coef = smooth_coef
    def update(self, v):
        if self.value is None:
            self.value = v
        else:
            c = self.smooth_coef
            self.value = c * self.value + (1.0-c) * v

