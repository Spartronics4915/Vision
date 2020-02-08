'''
Tests a wide variety of frames to find the average time it takes to solvePNP
'''
from pathlib import Path

import logging
import numpy as np
import algo
import config
import time
import cv2

cfg = config.moduleDebuggingConfig['algo']
top_dir = Path('data/1080p_test')
img_dir = [test_dir for test_dir in top_dir.glob('test_imgs_*')]
computationTimes = []
imgsProcessed = 0

logFmt = "%(name)-8s %(levelname)-6s %(message)s"
dateFmt = "%H:%M"
logging.basicConfig(level=logging.DEBUG,format=logFmt, datefmt=dateFmt)

logging.info("Began logger")



for test_dir in img_dir:
    fnames = [str(f) for f in test_dir.glob('*.png')]

    for f in fnames:
        frame = cv2.imread(f)
        initTime = time.monotonic()
        a, b = algo.realPNP(frame,cfg)
        finalTime = time.monotonic()
        computationTimes.append(finalTime-initTime)
        imgsProcessed += 1 

print("Total processing time: {}".format(sum(computationTimes)))
print("Average processing time: {}".format(sum(computationTimes)/imgsProcessed))
print("Images processed: {}".format(imgsProcessed))
