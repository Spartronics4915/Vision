"use strict";

const WebSocketServer = require('ws').Server;
const Splitter        = require('stream-split');
const merge           = require('mout/object/merge');
const NALseparator    = Buffer.from([0,0,0,1]);//NAL break

class ServerBase 
{
    constructor(server, options)
    {
        this.options = merge({
            width : 960,
            height: 540,
        }, options);
        this.wss = new WebSocketServer({ server });
        this.wss.on('connection', this._newClient.bind(this));
        this.wss.on("error", this._wsError.bind(this));
        this.readStream =  null;
    }

    getFeed(config)
    {
        throw new Error("to be implemented by subclasses");
    }

    endFeed()
    {
        console.log("endFeed isn't implemented by subclass");
    }

    _wsError(err)
    {
        console.error("websocket error: ", err);
    }

    _startFeed(cfg)
    {
        if(this.readStream == null)
        {
            var readStream = this.getFeed(cfg); // invokes subclass method
            readStream = readStream.pipe(new Splitter(NALseparator));
            readStream.on("data", this._broadcast.bind(this));
            this.readStream = readStream;
        }
    }

    _stopFeed(force)
    {
        if(force || this.wss.clients.length)
        {
            if(this.readStream != null)
            {
                this.readStream.end();
                this.readStream = null;
            }
            this.endFeed(force);
        }
    }

    _broadcast(data)
    {
        this.wss.clients.forEach(function(socket)
        {
            if(socket.buzy) return;
            socket.buzy = true;
            socket.buzy = false;
            socket.send(Buffer.concat([NALseparator, data]), { binary: true}, 
                function ack(error) { socket.buzy = false; });
        });
    }

    _newClient(socket) 
    {
        // clients are managed by this.www.clients
        console.log('New client');
        socket.send(JSON.stringify({
            action : "init",
            width  : this.options.width,
            height : this.options.height,
        }));
        socket.on("message", this._onClientMsg.bind(this));
        socket.on('close', this._onClientClose.bind(this));
    }

    _onClientMsg(data) 
    {
        var args = data.split(' ');
        var action = args[0];
        console.log("Incoming action '%s'", action);
        switch(action)
        {
        case "REQUESTSTREAM":
            this._startFeed(data);
            break;
        case "STOPSTREAM":
            this._stopFeed(); // was pause
            break;
        case "RESET":
            this._stopFeed(true);
            break;
        default:
            break;
        }
    }

    _onClientClose()
    {
        console.log('Client closed');
        this._stopFeed(true/*force*/);
    }
}

module.exports = ServerBase;
