#!/usr/bin/bash -f
export PYTHONUNBUFFERED=1
python calibrate.py --square_size=.837 "dbcam8/*/*.jpg"
