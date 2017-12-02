import datetime

class FPS:
    def __init__(self):
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        self._end = datetime.datetime.now()

    def update(self):
        self._numFrames += 1

    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        if self._end:
            return (self._end - self._start).total_seconds()
        else:
            return (datetime.datetime.now() - self._start).total_seconds()

    def getFPS(self):
        return self._numFrames / self.elapsed()

    def getFrameCount(self):
        return self._numFrames
