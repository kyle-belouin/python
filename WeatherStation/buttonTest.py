import RPi.GPIO as GPIO
import time

leftPin = 21 #pin21
rightPin = 22
upPin = 23
downPin = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # Numbers GPIOs by standard marking
GPIO.setup(leftPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(rightPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(upPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(downPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
while True:
    if 0 == GPIO.input(leftPin):
        print("left")
    if 0 == GPIO.input(rightPin):
        print("right")
    if 0 == GPIO.input(upPin):
        print("up")
    if 0 == GPIO.input(downPin):
        print("down")
    time.sleep(0.15)
