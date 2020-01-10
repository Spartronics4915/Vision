"use strict";

/**
* Run this on a raspberry pi 
* then browse (using google chrome/firefox) to http://[pi ip]:8080/
*/

const http = require('http');
const express = require('express');
const os = require('os');
const ifaces = os.networkInterfaces();
const WebStreamerServer = require('./serverRaspi');
const app = express();

//public website
app.use(express.static(__dirname + '/www'));
const server  = http.createServer(app);
const silence = new WebStreamerServer(server);
const ip = undefined;

// find our IPv4 address
Object.keys(ifaces).forEach(function (ifname) {
    ifaces[ifname].foreach(function(iface) {
        if(iface.family == "IPv4" && iface.internal == false)
        {
            if(ip == undefined)
            {
                ip = iface.address;
                return;
            }
            else
            {
                console.log("multiple ip addresses, ignoring: " +
                            iface.address);
            }
        }
    });
});

try
{
    console.log(`appRaspi listening on ${ip}:8080`);
    server.listen(8080, ip);
}

catch(err)
{
    console.log("appRaspi error: " + err.message);
    console.log("interfaces:\n" + JSON.stringify(ifaces, null, 2));
}

