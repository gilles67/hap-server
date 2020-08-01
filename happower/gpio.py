from threading import Thread, RLock
import RPi.GPIO as GPIO
import time
import sys

verrou = RLock()

def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(13, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(5, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(6, GPIO.OUT, initial=GPIO.HIGH)

def gpio_exit():
    GPIO.cleanup()

class PowerButton(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.continu = True
        self.attend = 20 / 1000

    def setClient(self, client):
        self.client = client

    def stop(self):
        self.continu = False
        self.join()

    def run(self):

        while self.continu:
            with verrou:
                time.sleep(self.attend)
            time.sleep(self.attend)

class PowerLed(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.continu = True;
        self.attend = 10 / 1000
        self.stat = "Off"
        self.lock_stat = ""

    def stop(self):
        self.continu = False
        self.join()

    def setLed(self, value):
        self.stat = value

    def run(self):
        while self.continu:
            with verrou:
                if self.stat != self.lock_stat:
                    if self.stat == "On":
                        GPIO.output(13, GPIO.LOW)
                    if self.stat == "Off":
                        GPIO.output(13, GPIO.HIGH)
                    self.lock_stat = self.stat
                if self.stat == "Blink":
                    GPIO.output(13, not GPIO.input(13))
                    self.lock_stat = self.stat
            time.sleep(self.attend)

def setAudioPower(value):
    with verrou:
        if value == "On":
            GPIO.output(6, GPIO.LOW)
        if value == "Off":
            GPIO.output(6, GPIO.HIGH)

def setAmpliPower(value):
    with verrou:
        if value == "On":
            GPIO.output(5, GPIO.LOW)
        if value == "Off":
            GPIO.output(5, GPIO.HIGH)
