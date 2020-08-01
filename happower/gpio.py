from threading import Thread, RLock
import RPi.GPIO as GPIO
import time
import sys

verrou = RLock()

def gpio_init():
    GPIO.setmode(gpio.BCM)
    GPIO.setup(19, gpio.IN, pull_up_down=gpio.PUD_UP)
    GPIO.setup(13, gpio.OUT, initial=gpio.HIGH)
    GPIO.setup(5, gpio.OUT, initial=gpio.HIGH)
    GPIO.setup(6, gpio.OUT, initial=gpio.HIGH)

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

def setAudioPower(value):
    if value:
        GPIO.output(6, gpio.LOW)
    else:
        GPIO.output(6, gpio.HIGH)

def setAmpliPower(value):
    if value:
        GPIO.output(5, gpio.LOW)
    else:
        GPIO.output(5, gpio.HIGH)
