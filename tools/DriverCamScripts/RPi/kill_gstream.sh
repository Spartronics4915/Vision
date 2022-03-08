#!/bin/bash


export killit=`ps -ef | grep gst-launch | grep -v grep | awk '{print $2}'`
kill -9 $killit
export killit2=`ps -ef | grep gstreamit.sh | grep -v grep | awk '{print $2}'`
kill -9 $killit2
