"use strict";

const http = require('http');
const express = require('express');

const RemoteTCPFeedRelay = require('staticServer');
const app = express();

//public website
app.use(express.static(__dirname + '/www'));

const server  = http.createServer(app);
var source1 = {
    width     : 480,
    height    : 270,
    video_path     : "samples/admiral.264",
    video_duration : 58,
};

var source2 = {
    width     : 960,
    height    : 540,
    video_path     : "samples/out.h264",
    video_duration : 58,
};

const feed = new RemoteTCPFeedRelay(server, source1);

server.listen(8080);



