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

    def __init__(self, client):
        Thread.__init__(self)
        self.client = client
        self.continu = True;
        self.attend = 20 / 1000

    def stop(self):
        self.continu = False
        self.join()

    def run(self):

        while self.continu:
            with verrou:
                time.sleep(self.attend)
            time.sleep(self.attend)

def setAudioPower(value):
    if value == "On":
        GPIO.output(6, GPIO.LOW)
    if value == "Off":
        GPIO.output(6, GPIO.HIGH)

def setAmpliPower(value):
    if value == "On":
        GPIO.output(5, GPIO.LOW)
    if value == "Off":
        GPIO.output(5, GPIO.HIGH)
