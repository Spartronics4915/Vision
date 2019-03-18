class App
{
    constructor()
    {
		document.addEventListener("DOMContentLoaded",
				this._onReady.bind(this), false);
        window.onbeforeunload = this._onBeforeUnload.bind(this);
    }

    _onReady()
    {
        this.statusEl = document.getElementById("status");
		this.canvasEl = document.getElementById("videocanvas");
		this.uri = "ws://" + document.location.host;
		this.wsavc = new WSAvcPlayer(this.canvasEl, "webgl", 1, 35);
        this.wsavc.connect(this.uri); // takes time, no callback
        this._onIdle();
    }

    _onIdle()
    {
        if(this.wsavc)
        {
            let txt = "undefined state";
            let st= this.wsavc.readyState();
            if(st != undefined)
            {
                txt = ["Connecting", "Open", 
                       "Closing", "Closed"][st];
            }
            this.statusEl.innerHTML = txt;
        }
        else
            this.statusEl.innerHTML = "no connection";

        setTimeout(this._onIdle.bind(this), 3000);
    }

    _onBeforeUnload()
    {
        this.disconnectWS();
    }

	playStream()
	{
		if(this.wsavc && !this.playing)
		{
            this.wsavc.playStream();
            this.playing = true;
		}
        if(document.activeElement)
            document.activeElement.blur();
	}

	stopStream()
	{
		if(this.wsavc && this.playing)
		{
			this.wsavc.stopStream();
			this.playing = false;
		}
        if(document.activeElement)
            document.activeElement.blur();
	}

	disconnectWS()
	{
		if(this.wsavc)
		{
			this.stopStream();
            setTimeout( function() {
                this.wsavc.disconnect();
            }.bind(this), 1000);
		}
        if(document.activeElement)
            document.activeElement.blur();
	}

    resetWS()
    {
		if(this.wsavc)
            this.wsavc.resetStream();
        if(document.activeElement)
            document.activeElement.blur();
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
