/**
* Run this on a raspberry pi 
* then browse (using google chrome/firefox) to http://[pi ip]:5085/
*/
const port = 5805; // legal port for competition FMS
const http = require('http');
const express = require('express');
const WebStreamerServer = require('./serverRaspi');
const os = require('os');

doit();

function doit()
{
    let ip = getIP();

    const app = express();
    const server  = http.createServer(app);
    const silence = new WebStreamerServer(server);
    app.use(express.static(__dirname + '/www')); // public website

    // start the server on a single interface
    try
    {
        console.log(`appRaspi listening on ${ip}:${port}`);
        server.listen(port, ip); // 
    }

    catch(err)
    {
        console.log("appRaspi error: " + err.message);
    }
}

function getIP()
{
    // find our IPv4 address
    const ifaces = os.networkInterfaces();
    let ip = undefined;

    console.log("host interfaces discovered:");
    for(let ifname of Object.keys(ifaces))
    {
        for(let iface of ifaces[ifname])
        {
            console.log(`  ${ifname} ${iface.family} ip:${iface.address}`);
            if(iface.family == "IPv4" && iface.internal == false)
            {
                if(ip == undefined)
                {
                    ip = iface.address;
                }
                else
                {
                    console.log("   Multiple IPv4 addresses, ignoring: " +
                                iface.address);
                }
            }
        }
    }
    return ip;
}
