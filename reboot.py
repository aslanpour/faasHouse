#!/usr/bin/env python3
#connect a female wire to Pin 17 of a controller Pi 3 (only worked on Pi 3) on one end and a the male end to the 'Run' pin/hole of the Pi 3 that is going to be restarted.
#Run this code on the controller Pi to restart the other Pi.
#if not, run as sudo

import RPi.GPIO as GPIO
import time
PIN=17
GPIO.setmode(GPIO.BCM)  # set the pin numbering scheme to BCM
GPIO.setup(PIN, GPIO.OUT)  # set up GPIO 17 as an output

GPIO.output(PIN, GPIO.LOW)  # trigger the restart by pulling GPIO 17 low
time.sleep(1)  # wait for 1 second
GPIO.output(PIN, GPIO.HIGH)  # release GPIO 17 to allow the Raspberry Pi to start up
# release the GPIO channel
GPIO.cleanup(PIN)