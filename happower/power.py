from mpd import MPDClient
from gpio import setAudioPower, setAmpliPower
from happower import pled
from threading import Thread, RLock
import time
import sys
import json

pm_verrou = RLock()

class PowerManagement(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.continu = True
        self.attend = 500 / 1000
        self.seq_lock = False
        self.seq_name = None
        self.seq_progress = 0
        self.counter = 0
        self.client = None
        self.current_state = "Off"
        self.mpd = MPDClient()

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
            
    def TogglePower(self):
        if self.current_state == "Off":
            self.OnSequence()
        if self.current_state == "On":
            self.OffSequence()

    def OnSequence(self):
        if self.seq_lock:
            return False
        self.seq_lock = True
        self.seq_name = "On"
        self.seq_progress = 0
        self.counter = 0

    def OffSequence(self):
        if self.seq_lock:
            return False
        self.seq_lock = True
        self.seq_name = "Off"
        self.seq_progress = 0
        self.counter = 0

    def publishStatus(self):
        status = {'sequence': self.seq_name, 'progress': self.seq_progress }
        self.client.publish('hap/power/status', json.dumps(status))

    def EndSequence(self):
        self.publishStatus()
        self.seq_lock = False
        self.seq_name = None
        self.seq_progress = 0
        self.counter = 0

    def run(self):
        self.mpd.timeout = 10
        self.mpd.idletimeout = None
        self.mpd.connect("localhost", 6600)
        while self.continu:
            with pm_verrou:
                if self.seq_lock:
                    self.counter += 1
                    #sys.stdout.write(str(self.counter))
                    #sys.stdout.flush()
                    if self.seq_name == "On":
                        if self.counter == 1:
                            self.seq_progress = 1
                            setAudioPower('On')
                            pled.setLed("Blink")
                            self.publishStatus()
                        if self.counter == 10:
                            self.seq_progress = 2
                            setAmpliPower('On')
                            self.publishStatus()
                        if self.counter == 14:
                            self.seq_progress = 3
                            self.current_state = "On"
                            pled.setLed("On")
                            self.EndSequence()
                    if self.seq_name == "Off":
                        if self.counter == 1:
                            self.seq_progress = 1
                            setAmpliPower('Off')
                            pled.setLed("Blink")
                            self.publishStatus()
                        if self.counter == 8:
                            self.seq_progress = 2
                            setAudioPower('Off')
                            self.publishStatus()
                        if self.counter == 18:
                            self.seq_progress = 3
                            self.current_state = "Off"
                            pled.setLed("Off")
                            self.EndSequence()
            time.sleep(self.attend)
