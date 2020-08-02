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

    def setClient(self, client):
        self.client = client

    def stop(self):
        self.continu = False
        self.join()

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
        while self.continu:
            with pm_verrou:
                if self.seq_lock:
                    self.counter += 1
                    if self.seq_name == "On":
                        if self.counter == 1:
                            self.seq_progress = 1
                            setAudioPower('On')
                            pled.setLed("Blink")
                            self.publishStatus()
                        if self.counter == 4:
                            self.seq_progress = 2
                            setAmpliPower('On')
                            self.publishStatus()
                        if self.counter == 8:
                            self.seq_progress = 3
                            self.EndSequence()

            time.sleep(self.attend)
