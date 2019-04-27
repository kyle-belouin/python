import subprocess
import time

def networkCheck():
    percentIndex = 0
    #Thanks to https://www.raspberrypi.org/forums/viewtopic.php?t=124240 !
    print("Pinging an Internet IP")
    pingOutput = str(subprocess.check_output(["ping", "8.8.8.8", "-c", "5"]))
    percentIndex = pingOutput.find('%')
    percentFailed = int(pingOutput[percentIndex - 1])
    print("Loss rate: " + str(percentFailed) + "%")
    if percentFailed == 0:
        print("Connection is perfect")
    elif percentFailed >1 and percentFailed <40:
        print("Connection is lossy")
    elif percentFailed >40 and percentFailed <75:
        print("Connection is poor")
    elif percentFailed >75:
        print("No connection to the Internet")

    time.sleep(2)
    print("Pinging a website")
    pingOutput = str(subprocess.check_output(["ping", "www.weather.com", "-c", "5"]))
    percentIndex = pingOutput.find('%')
    percentFailed = int(pingOutput[percentIndex - 1])
    print("Loss rate: " + str(percentFailed) + "%")
    if percentFailed == 0:
        print("Connection is perfect")
    elif percentFailed >1 and percentFailed <40:
        print("Connection is lossy")
    elif percentFailed >40 and percentFailed <75:
        print("Connection is poor")
    elif percentFailed >75:
        print("No connection to the location")

networkCheck()
