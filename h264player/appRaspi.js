"use strict";

/**
* Run this on a raspberry pi 
* then browse (using google chrome/firefox) to http://[pi ip]:8080/
*/

const http = require('http');
const express = require('express');
const WebStreamerServer = require('./raspiServer');
const app = express();

//public website
app.use(express.static(__dirname + '/www'));
const server  = http.createServer(app);
const silence = new WebStreamerServer(server);

server.listen(8080);
