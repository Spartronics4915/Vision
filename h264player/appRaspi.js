"use strict";

/**
* Run this on a raspberry pi 
* then browse (using google chrome/firefox) to http://[pi ip]:8080/
*/

const os = require('os');
const ifaces = os.networkInterfaces();
const http = require('http');
const express = require('express');
const os = require('os');
const ifaces = os.networkInterfaces();
const WebStreamerServer = require('./serverRaspi');
const app = express();
let ip = undefined;

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

// find our IPv4 address
console.log("interfaces:\n");
for(let ifname of Object.keys(ifaces))
{
    for(let iface of ifaces[ifname])
    {
        console.log(`${ifname} ${iface.family} ip:${iface.address}`);
        if(iface.family == "IPv4" && iface.internal == false)
        {
            if(ip == undefined)
            {
                ip = iface.address;
            }
            else
            {
                console.log("multiple ip addresses, ignoring: " +
                        iface.address);
            }
        }
    }
}

try
{
    console.log(`appRaspi listening on ${ip}:5805`);
    server.listen(5805, ip); // 
}

catch(err)
{
    console.log("appRaspi error: " + err.message);
}
