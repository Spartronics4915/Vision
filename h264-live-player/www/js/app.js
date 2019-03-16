class App
{
    constructor()
    {
		document.addEventListener("DOMContentLoaded",
				this._onReady.bind(this), false);
    }

    _onReady()
    {
		this.canvas = document.getElementById("videocanvas");
		this.uri = "ws://" + document.location.host;
		this.wsavc = new WSAvcPlayer(this.canvas, "webgl", 1, 35);
        this.wsavc.connect(this.uri); // takes time, no callback
    }

	playStream()
	{
		if(this.wsavc && !this.playing)
		{
            this.wsavc.playStream();
            this.playing = true;
		}
	}

	stopStream()
	{
		if(this.wsavc && this.playing)
		{
			this.wsavc.stopStream();
			this.playing = false;
		}
	}

	disconnectWS()
	{
		if(this.wsavc)
		{
			this.stopStream();
			this.wsavc.disconnect();
		}
	}

    logMsg(msg)
    {
        console.log(msg);
    }

    debug(msg)
    {
        if(this.config.debug)
            this.logMsg("DEBUG   " + msg);
    }

    info(msg)
    {
        this.logMsg("INFO    " + msg);
    }

    notice(msg)
    {
        this.logMsg("NOTICE  " + msg);
    }

    warning(msg)
    {
        this.logMsg("WARNING " + msg);
    }

    error(msg)
    {
       // todo add alert?
        this.logMsg("ERROR " + msg);
    }

}

window.app = new App();
