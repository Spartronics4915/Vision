#!/usr/bin/bash -f
export PYTHONUNBUFFERED=1
python3 calibrate.py --square_size=.7656 "GPCalib/*/*.jpg"
