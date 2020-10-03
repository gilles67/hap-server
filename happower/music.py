from mpd import MPDClient
from threading import Thread, RLock
import time
import sys
import json

md_verrou = RLock()

class MusicManagement(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.continu = True
        self.mpd = MPDClient()
        self.mpd.timeout = 10
        self.mpd.idletimeout = None
        self.wait_time = 1

    def setClient(self, client):
        self.client = client

    def stop(self):
        self.continu = False
        self.join()
        try:
            self.mpd.close()
            self.mpd.disconnect()
        except:
            pass
    def mpdConnect(self):
        try:
            self.mpd.ping()
        except:
            self.mpd.connect("localhost", 6600)

    def command(self, payload):
        self.mpdConnect()
        if payload == 'pause':
            self.mpd.pause(1)
        if payload == 'play':
            self.mpd.pause(0)
        if payload == 'stop':
            self.mpd.stop()

    def publishStatus(self):
        status = { 'status': self.mpd.status(), 'song': self.mpd.currentsong()}
        self.client.publish('hap/music/status', json.dumps(status))

    def run(self):
        while self.continu:
            try:
                self.mpdConnect()
                self.publishStatus()
            except Exception as err:
                print("MPD Error")
                print(err)

            time.sleep(self.wait_time)
