#!/usr/bin/env python
#This is a game! You have to press the button to stop the light from flashing.
#If you press the button and the light is lit, you will get a point!
#If you press the button and the light is off, you will lose a point!
#The LEDs that are not blinking indicate your score.
#When you get all three LEDs lit, you have won the game!
#When you get your fourth point, your score will return to 0 (lights off) so you may keep playing!
#Code by David Sommerfeld and Kyle Belouin

import RPi.GPIO as GPIO
import time

leftPin = 21 #pin21
rightPin = 22
upPin = 23
downPin = 24
#ButtonPin = 18 #pin18
#LightStatus = False
#score = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # Numbers GPIOs by standard marking
GPIO.setup(leftPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(rightPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(upPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(downPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
while True:
#Using a while loop to both blink the LED and take note of the
#state of the LED as well as controlling the behavior of the button
    if 0 == GPIO.input(leftPin):
        print("left")
    if 0 == GPIO.input(rightPin):
        print("right")
    if 0 == GPIO.input(upPin):
        print("up")
    if 0 == GPIO.input(downPin):
        print("down")
    #else:
    #    print("not working")
    time.sleep(0.15)
