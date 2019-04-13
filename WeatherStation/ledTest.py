#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import random

greenLed = 17 # pin17
blueLed = 18 # pin22
redLed = 19 # pin23
whiteLed = 20 # pin24

ledList = [greenLed, blueLed, redLed, whiteLed]

GPIO.setmode(GPIO.BCM)      # Numbers GPIOs by standard marking
GPIO.setup(ledList, GPIO.OUT) # Set LedPin's mode is output
GPIO.output(ledList, GPIO.HIGH) # Set LedPin high(+3.3V) to turn off led
GPIO.setwarnings(False)

i = 0
while True:
    #print('...led on')
    i = random.randint(0, 3)
    GPIO.output(ledList[i], GPIO.LOW) # led on
    time.sleep(0.2)
    #print('led off...')
    GPIO.output(ledList[i], GPIO.HIGH) # led off
    #time.sleep(0.02)
