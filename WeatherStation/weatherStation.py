#Title: Raspberry Pi Weather Station
#Purpose: COMP430 Final Project
#Author: Kyle Belouin, external libraries used

import datetime
import time
import urllib.request
import smbus
import subprocess
import os
import random
import RPi.GPIO as GPIO

#GPIO assignments
#LED assignments
tempLed = 17 #green
winterLed = 18 #blue
alertLed = 19 #red
conditionLed = 20 #white
#buttons
leftPin = 21
rightPin = 22
upPin = 23
downPin = 24
buttons = [21, 22, 23, 24]

ledList = [tempLed, winterLed, alertLed, conditionLed]
ledOn = GPIO.LOW
ledOff = GPIO.HIGH

#ledSetup
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledList, GPIO.OUT)
GPIO.output(ledList, GPIO.HIGH)
GPIO.setwarnings(False)

#buttonSetup
GPIO.setup(buttons, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#LCD pin assignments, constants, etc
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable it

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# LCD commands
LCD_CMD_4BIT_MODE = 0x28   # 4 bit mode, 2 lines, 5x8 font
LCD_CMD_CLEAR = 0x01
LCD_CMD_HOME = 0x02   # goes to position 0 in line 0
LCD_CMD_POSITION = 0x80  # Add this to DDRAM address

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
    lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
    lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    # 0 for command

    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
    time.sleep(E_DELAY)

def lcd_string(message,line):
    # Send string to display
    message = message.ljust(LCD_WIDTH," ")
    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)

# functions not in the original library
# -------------------------------------

# Positions the cursor so that the next write to the LCD
# appears at a specific row & column, 0-org'd
def lcd_xy(col, row):
    lcd_byte(LCD_CMD_POSITION+col+(64*row), LCD_CMD)

# Begins writing a string to the LCD at the current cursor
# position. It doesn't concern itself with whether the cursor
# is visible or not. Go off the screen? Your bad.
def lcd_msg(msg_string):
    for i in range(0, len(msg_string)):
        lcd_byte(ord(msg_string[i]), LCD_CHR)

 
def webRead(URL):
    try:
        h = urllib.request.urlopen(URL)
        response = h.read()       
    except:
        print("Page failed to load. Ensure you didn't enter an invalid zip code or check the network.")
        lcd_init()
        lcd_string("Failed to load.", LCD_LINE_1)
        lcd_string("Check zipcode...", LCD_LINE_2)
        time.sleep(3)
        lcd_string("or check network", LCD_LINE_2)
        time.sleep(3)
        lcd_init()
        lcd_string("Loading settings...", LCD_LINE_1)
        time.sleep(2)
        response = ""
        userSetup()
        theProgram()#starting over from the beginning

    return response

def getTime():
    timeQuery = str(subprocess.Popen("date", shell=True, stdout=subprocess.PIPE).stdout.read()) #gets system time
    cleanupList = ["b'", "n'", "\\"]
    i = 0
    while i <= 2: #gritty cleanup for unwanted chars from above query
        timeQuery = timeQuery.replace(cleanupList[i], "")
        i += 1
    print("Time: " + timeQuery)

#Possible units of measure
units=["metric", "imperial"]
pressureUnits = ["millibars", "inches of Hg"]
tempUnits = ["C", "K", "F"]

#call from external settings file
def getSettings(): 
    global settings 
    settings = open('/home/kpb/git/python/WeatherStation/settings.cfg', 'r')
    global unit
    global pressureUnit
    global tempUnit
    global zipcode
    global refreshRate
    unit = units[(int((settings.readline())))] #line 1 in settings.cfg corresponds to units
    pressureUnit = pressureUnits[(int((settings.readline())))] #line 2 for pressureUnits  
    tempUnit = tempUnits[(int((settings.readline())))] #line 3 for tempUnits
    zipcode = settings.readline() #line 4 holds zipcode 
    zipcode = zipcode.replace("\n","")#had to remove an undesired newline
    refreshRate = int(settings.readline()) #line 5 is the refresh rate
    return unit
    return pressureUnit
    return tempUnit
    return zipcode
    return settings
    return refreshRate
    settings.close()#we're done here, close the file

def getZipcode():
    k = 0
    selector = "^"
    with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'r') as file:
        line = file.readlines()
    file.close()
    zipcode = (line[3])
    zipcode = zipcode.replace('\n' , "") #there's a newline that has to be dropped

    #splitting up the digits into individual integers
    zc1 = int(zipcode[0])
    zc2 = int(zipcode[1])
    zc3 = int(zipcode[2])
    zc4 = int(zipcode[3])
    zc5 = int(zipcode[4])

    while True:
        zipcode = (str(zc1) + str(zc2) + str(zc3) + str(zc4) + str(zc5))               
        lcd_string(zipcode, LCD_LINE_1)
        lcd_string(selector, LCD_LINE_2)
        if 0 == GPIO.input(upPin):
            if k == 0:
                if zc1 >= 9: #if we go over 9, reset to 0
                    zc1 = 0
                else:
                    zc1 += 1
            if k == 1:
                if zc2 >= 9:
                    zc2 = 0
                else:
                    zc2 += 1
            if k == 2:
                if zc3 >= 9:
                    zc3 = 0
                else:
                    zc3 += 1
            if k == 3:
                if zc4 >= 9:
                    zc4 = 0
                else:
                    zc4 += 1
            if k == 4:
                if zc5 >= 9:
                    zc5 = 0
                else:
                    zc5 += 1

        if 0 == GPIO.input(downPin):
            if k == 0:
                if zc1 <= 0: #if we go below 0, reset to 9
                    zc1 = 9
                else:
                    zc1 -= 1
            if k == 1:
                if zc2 <= 0:
                    zc2 = 9
                else:
                    zc2 -= 1
            if k == 2:
                if zc3 <= 0:
                    zc3 = 9
                else:
                    zc3 -= 1
            if k == 3:
                if zc4 <= 0:
                    zc4 = 9
                else:
                    zc4 -= 1
            if k == 4:
                if zc5 <= 0:
                    zc5 = 9
                else:
                    zc5 -= 1

        if 0 == GPIO.input(rightPin): #moves selector to the right
            k += 1
            if k >= 5:
                selector = "^" #move back to starting position
                k = 0
            else:
                selector = (" " + selector) #one space for the increment

        if 0 == GPIO.input(leftPin):
            line[3] = (zipcode + '\n') #\n for new line
            for a, l in enumerate(line): #gets how many lines are in the file. Using 'a' is arbitrary
                pass
            x = 0 
            with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'w') as file:
                while x <= a: #we have to rebuild the whole file, so writing it back line by line with the change we want plus the same info we already had. There is probably a better way to do this
                    file.writelines(line[x])
                    x += 1
                file.close()
            lcd_string("Saved!", LCD_LINE_2)
            time.sleep(2)
            return #leave this function

def setRefreshRate():
    with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'r') as file:
        line = file.readlines()
        file.close()
    rate = int(line[4])
    
    while True:
        lcd_string("Left to save", LCD_LINE_2)
        if rate == 60:
            lcd_string((str(int(rate / 60)) + " minute"), LCD_LINE_1)
        if rate > 60 and rate < 3600:
            lcd_string((str(int(rate / 60)) + " minutes"), LCD_LINE_1)
        if rate < 60:
            lcd_string((str(rate) + " seconds"), LCD_LINE_1)
        if rate == 3600:
            lcd_string((str(rate / 3600) + " hour"), LCD_LINE_1)
        if rate > 3600 and rate < 86400:
            lcd_string((str(round((rate / 3600), 2)) + " hours"), LCD_LINE_1)
        if rate == 86400:
            lcd_string((str(int(rate / 86400)) + " day"), LCD_LINE_1)
        if rate > 86400:
            lcd_string((str(round((rate / 86400), 2)) + " days"), LCD_LINE_1)
                
        if 0 == GPIO.input(upPin):
            time.sleep(0.05)
            if rate >= 10 and rate < 60:
                rate = rate + 10
            elif rate >= 60 and rate < 3600:
                rate = rate + 60
            elif rate >= 3600 and rate < 86400:
                rate = rate + 900
            elif rate >= 86400:
                rate = rate + 21600

        if 0 == GPIO.input(downPin):
            time.sleep(0.05)
            if rate > 10 and rate <= 60:
                rate = rate - 10
            elif rate >= 60 and rate < 3600:
                rate = rate - 60
            elif rate >= 3600 and rate < 86400:
                rate = rate - 900
            elif rate >= 86400:
                rate = rate - 21600

        if 0 == GPIO.input(leftPin):
            line[4] = (str(rate) + '\n')
            for a, l in enumerate(line): 
                pass
            x = 0 
            with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'w') as file:
                while x <= a: 
                    file.writelines(line[x])
                    x += 1
                file.close()
            lcd_string("Saved!", LCD_LINE_2)
            time.sleep(2)
            return #leave this function

def networkCheck():
    #Thanks to https://www.raspberrypi.org/forums/viewtopic.php?t=124240 !
    lcd_init()
    percentIndex = 0
    print("####################")
    print("Running network check...")
    print("Pinging an Internet IP")
    lcd_string("Pinging 8.8.8.8", LCD_LINE_1)
    pingOutput = str(subprocess.check_output(["ping", "8.8.8.8", "-c", "5"]))
    percentIndex = pingOutput.find('%')
    percentFailed = int(pingOutput[percentIndex - 1])
    print("Loss rate: " + str(percentFailed) + "%")
    lcd_string(("Loss rate: " + str(percentFailed) + "%"), LCD_LINE_1)
    if percentFailed == 0:
        print("Connection is perfect")
        lcd_string("No issues", LCD_LINE_2)
    elif percentFailed >1 and percentFailed <40:
        print("Connection lossy")
        lcd_string("Connection is loss", LCD_LINE_2)
    elif percentFailed >40 and percentFailed <75:
        print("Connection is poor")
        lcd_string("Connection poor", LCD_LINE_2)     
    elif percentFailed >75:
        print("No connection to the Internet")
        lcd_string("No connection", LCD_LINE_2)

    time.sleep(5)
               
    lcd_init()
    percentIndex = 0
    print("Running network check...")
    print("Pinging a website (name resolution check)")
    lcd_string("Checking DNS", LCD_LINE_1)
    lcd_string("Pinging website", LCD_LINE_2)
    pingOutput = str(subprocess.check_output(["ping", "www.weather.com", "-c", "5"]))
    percentIndex = pingOutput.find('%')
    percentFailed = int(pingOutput[percentIndex - 1])
    print("Loss rate: " + str(percentFailed) + "%")
    lcd_string(("Loss rate: " + str(percentFailed) + "%"), LCD_LINE_1)
    if percentFailed == 0:
        print("Connection is perfect")
        lcd_string("No issues", LCD_LINE_2)
    elif percentFailed >1 and percentFailed <40:
        print("Connection is lossy")
        lcd_string("Connection loss", LCD_LINE_2)
    elif percentFailed >40 and percentFailed <75:
        print("Connection poor")
        lcd_string("Connection is poor", LCD_LINE_2)     
    elif percentFailed >75:
        print("No connection to the Internet")
        lcd_string("No connection", LCD_LINE_2)
    time.sleep(5)

    lcd_string("Left to exit", LCD_LINE_2)

    while True:
        if 0 == GPIO.input(leftPin):
            lcd_string("Exiting", LCD_LINE_2)
            time.sleep(0.25)
            break
    return

def buildUrl(): #This searches for a zip and then navigates to a corresponding weather page; builds a URL to go to.
    global url
    url = str("https://weather.com/weather/today/l/" + zipcode) 
    return url

def getWeather():
    lcd_init()
    lcd_string("Gathering data...", LCD_LINE_1)
    i = 0 #little loading animation with the lights
    while True: 
        GPIO.output(ledList[i], ledOn)
        time.sleep(0.5)
        i += 1
        if i >= 4:
            i -= 1
            break
    while True:
        GPIO.output(ledList[i], ledOff)
        time.sleep(0.05)
        i -= 1
        if i <= 0:
            GPIO.output(ledList[0], ledOff)
            break

    global webpage
    global zipMsg
    lcd_string("Processing data...", LCD_LINE_1)
    webpage = (str(webRead(url)))
    #Save to file
    file = open('webpageout.txt', 'w')
    file.write(str(webpage))
    file.close()
    zipMsg = ("Current weather for " + zipcode)
    print(zipMsg)
    return webpage
    return zipMsg

def getTemp():
    #Finding temperature
    tempIndex = webpage.find(('class="today_nowcard-temp"'))
    tempIndex = webpage.find('class=""', tempIndex)
    tempIndex = webpage.find('>', tempIndex) + 1
    endTempIndex = webpage.find('<', tempIndex) - 1
    temp = []
    difference = endTempIndex - tempIndex
    global tempInt
    global tempString
    i = 0 
    while i <= difference: #puts values into array... 
        temp.append (webpage[tempIndex + i])
        i += 1
    tempInt = int((temp[0] + temp[1])) #...then converts those two numbers into integers.
#unit conversions
    if (tempUnit == tempUnits[0]):#Celcius
        tempInt = round(((tempInt - 32) * (5/9)), 1)
        tempString = ("Temp: " + (str(tempInt)) + "C")
        print(tempString)
    elif (tempUnit == tempUnits[1]):#Kelvin...for the nerds.
        tempInt = round(((tempInt - 32) * (5/9) + 273.15), 2)
        tempString = ("Temp: " + (str(tempInt)) + "K")
        print(tempString)
    else: #Fahrenheit
        tempString = ("Temp: " + (str(tempInt)) + "F")
        print(tempString)
    return tempInt
    return tempString

def getWind():
    #Finding windspeed
    windIndex = webpage.find(('th>Wind'))
    windIndex = webpage.find('class=""', windIndex)
    windIndex = webpage.find('>', windIndex) + 1
    endWindIndex = webpage.find('mph', windIndex) - 1
    difference = endWindIndex - windIndex
    wind = []
    global windInt
    global direction
    global windString
    windInt = 0
    i = 0
    while i < difference:
        wind.append (webpage[windIndex + i])
        i += 1
    space = wind.index(' ') #there is a space in the list that separates direction from speed value. Finding where this is.
    if "C" in wind:
        windInt = 0
        direction = ""
        speedUnit = ""
    else:
        windInt = int(wind[space + 1]) #temperature will always be one index ahead of the space
        if unit == "metric":
            windInt = round((windInt * 1.60934), 0)
            speedUnit = "Km/h"
        else:
            speedUnit = "MPH"
    #Finding wind direction
        windDirIndex = space - space #return index to 0
        windDir = []
        i = 0
        while i <= space:
            windDir.append (wind[windDirIndex + i])
            i += 1
        direction = ''.join(map(str,windDir)) #Joining the elements of a list together. String joining discovered here https://www.programiz.com/python-programming/methods/string/join
    windString = ("Wind: " + (str(windInt)) + speedUnit + " " + direction)
    print(windString)
    return windInt
    return direction
    return windString
   
def getConditions(): 
    #Finding conditions
    global currentConditions
    global conditionString
    conditionIndex = webpage.find(('class="today_nowcard-phrase"'))
    conditionIndex = webpage.find(('>'), conditionIndex) + 1
    endIndex = webpage.find('<', conditionIndex) - 1
    webpageConditions = []
    stringLength = endIndex - conditionIndex
    i = 0
    while i <= stringLength:
        webpageConditions.append (webpage[conditionIndex + i])
        i += 1
    currentConditions = ''.join(map(str,webpageConditions))#turning the webpageConditions list into string
    conditionString = ("Conditions: " + currentConditions)
    print(conditionString)
    return currentConditions
    return conditionString

def getHumidity():
    #Finding humidity
    global humidityString
    humidityIndex = webpage.find('th>Humidity')
    humidityIndex = webpage.find('class=""', humidityIndex)
    humidityIndex = webpage.find('span', humidityIndex)
    humidityIndex = webpage.find('>', humidityIndex) + 1
    endHumidityIndex = webpage.find('<', humidityIndex) - 1
    difference = endHumidityIndex - humidityIndex
    humidity = []
    i = 0
    while i <= difference:
        humidity.append (webpage[humidityIndex + i])
        i += 1
    humidityPercent = int((humidity[0] + humidity[1]))
    humidityString = ("Humidity: " + (str(humidityPercent) + "%"))
    print(humidityString)

def getDewPoint():
    global dpString
    dpIndex = webpage.find('th>Dew Point')
    dpIndex = webpage.find('class=""', dpIndex)
    dpIndex = webpage.find('>', dpIndex) + 1
    endDpIndex = webpage.find('<', dpIndex) - 1
    difference = endDpIndex - dpIndex 
    dewPoint = []
    i = 0
    while i <= difference:
        dewPoint.append (webpage[dpIndex + i])
        i += 1
    dewPoint = ''.join(map(str,dewPoint))
    dewPointInt = int(dewPoint)
    if (tempUnit == tempUnits[0]):#Celcius
        dewPointInt = round(((dewPointInt - 32) * (5/9)), 1)
        dpString = ("Dew Point: " + (str(dewPointInt)) + "C")
        print(dpString)
    elif (tempUnit == tempUnits[1]):#Kelvin...for the nerds.
        dewPointInt = round(((dewPointInt - 32) * (5/9) + 273.15), 2)
        dpString = ("Dew Point: " + (str(dewPointInt)) + "K")
        print(dpString)
    else: #Fahrenheit
        dpString = ("Dew Point: " + (str(dewPointInt)) + "F")
        print(dpString)
    return dpString

def getPressure():
    #Finding barometric pressure
    global pressureString
    pressureIndex = webpage.find('th>Pressure')
    pressureIndex = webpage.find('class=""', pressureIndex)
    pressureIndex = webpage.find('>', pressureIndex) + 1
    endPressureIndex = webpage.find('in', pressureIndex) - 1
    difference = endPressureIndex - pressureIndex
    pressure = []
    i = 0
    while i <= difference:
        pressure.append (webpage[pressureIndex + i])
        i += 1
    pressure = ''.join(map(str,pressure)) #turning the list into a string...
    pressure = float(pressure) #...then to an float
    if pressureUnit == pressureUnits[0]:
        pressure = round((pressure * 33.8639), 1) #conversion to millibars
        pressureString = ("Pressure: " + (str(pressure)) + "mbar")
        print(pressureString)
    else:
        pressureString = ("Pressure: " + (str(pressure)) + "in. Hg")
        print(pressureString)
    return pressureString

def getAlerts(): 
    global activeAlert
    global alertString
    alertIndex = webpage.find('class="SevereAlertBar"')
    if alertIndex == -1: #no response condition
        activeAlert = "None" 
        alertString = ("No alerts")
        print(alertString)
    else: 
        alertIndex = webpage.find('title="', alertIndex)
        alertIndex = webpage.find('"', alertIndex) + 1
        endAlertIndex = webpage.find('"', alertIndex) - 1
        difference = endAlertIndex - alertIndex
        alert = []
        i = 0
        while i <= difference:
            alert.append (webpage[alertIndex + i])
            i += 1
        activeAlert = ''.join(map(str,alert)) 
        alertString = ("Alert: " + activeAlert)
        print(alertString)
    return alertString
    return activeAlert

ledCurTime = time.time()
condCurTime = time.time()
alertCurTime = time.time()

def processLeds():
    global ledCurTime #reference above global var otherwise, python really wants a local variable defined somewhere in this function for the usage below
    global condCurTime
    global alertCurTime
    difference = time.time() - ledCurTime
    condDifference = time.time() - condCurTime
    alertDifference = time.time() - alertCurTime
#process for temperature
    if tempUnit == "C": #different thresholds for different light activity
        if tempInt < 4.5:     
            if difference < 3:
                GPIO.output(tempLed, ledOn)
            if difference >= 3:
                GPIO.output(tempLed, ledOff)
            if difference >= 6:
                ledCurTime = time.time()
         
        if tempInt > 4.5 and tempInt < 12.8:
            if difference < 2:
                GPIO.output(tempLed, ledOn)
            if difference >= 2:
                GPIO.output(tempLed, ledOff)
            if difference >= 4:
                ledCurTime = time.time()

        if tempInt > 12.8 and tempInt < 21.1:
            GPIO.output(tempLed, ledOn)

        if tempInt > 21.1:
            if difference < 1:
                GPIO.output(tempLed, ledOn)
            if difference >= 1:
                GPIO.output(tempLed, ledOff)
            if difference >= 2:
                ledCurTime = time.time()

    if tempUnit == "F":
        if tempInt < 40:
            if difference < 3:
                GPIO.output(tempLed, ledOn)
            if difference >= 3:
                GPIO.output(tempLed, ledOff)
            if difference >= 6: 
                ledCurTime = time.time()

        if tempInt > 40 and tempInt < 55:
            if difference < 2:
                GPIO.output(tempLed, ledOn)
            if difference >= 2:
                GPIO.output(tempLed, ledOff)
            if difference >= 4:
                ledCurTime = time.time()
        
        if tempInt > 55 and tempInt < 70:
            GPIO.output(tempLed, ledOn)
        
        if tempInt > 70:
            if difference < 1:
                GPIO.output(tempLed, ledOn)
            if difference >= 1:
                GPIO.output(tempLed, ledOff)
            if difference >= 2:
                ledCurTime = time.time()
    
    if tempUnit == "K":
        if tempInt < 277.594:
            if difference < 3:
                GPIO.output(tempLed, ledOn)
            if difference >= 3:
                GPIO.output(tempLed, ledOff)
            if difference >= 6: 
                ledCurTime = time.time()

        if tempInt > 277.594 and tempInt < 285.928:
            if difference < 2:
                GPIO.output(tempLed, ledOn)
            if difference >= 2:
                GPIO.output(tempLed, ledOff)
            if difference >= 4:
                ledCurTime = time.time()
        
        if tempInt > 285.928 and tempInt < 294.261:
            GPIO.output(tempLed, ledOn)
        
        if tempInt > 294.261:
            if difference < 1:
                GPIO.output(tempLed, ledOn)
            if difference >= 1:
                GPIO.output(tempLed, ledOff)
            if difference >= 2:
                ledCurTime = time.time()

#process for conditions incl winter
    possibleConditions = ["Clear", "Sunny", "Mostly Sunny", "Partly Cloudy", "Fair", "Cloudy", "Mostly Cloudy", "Overcast", "Showers", "Light Rain", "Rain", "Rain Shower", "Heavy Rain", "Thunderstorm", "Light Snow", "Snow Shower", "Snow", "Sleet", "Freezing Rain", "Ice"] #dirty, but these are a list of common conditions plus a few odd ones weather.com threw my way.

    if currentConditions in possibleConditions:
        conditionIndex = possibleConditions.index(currentConditions)
        if conditionIndex <= 4: #sunny, etc
            GPIO.output(conditionLed, ledOn)
        elif conditionIndex >= 5 and conditionIndex <= 7: #cloudy
            if condDifference < 1:
                GPIO.output(conditionLed, ledOn)
            if condDifference >= 1:
                GPIO.output(conditionLed, ledOff)
            if condDifference >= 2:
                condCurTime = time.time()
        elif conditionIndex >= 8 and conditionIndex <= 12: #rain of some sort 
            if condDifference < 2:       
                GPIO.output(conditionLed, ledOn)
            if condDifference >= 2:    
                GPIO.output(conditionLed, ledOff)
            if condDifference >= 4:          
                condCurTime = time.time()
        elif conditionIndex == 13: #water is falling from the sky, likely at a high rate and with electrostaic discharges
           if condDifference < 0.5:
               GPIO.output(conditionLed, ledOn)
           if condDifference >= 0.5:
               GPIO.output(conditionLed, ledOff)
           if condDifference >= 1:
               condCurTime = time.time()
        elif conditionIndex >= 14 and conditionIndex <= 16: #snowing!
            GPIO.output(winterLed, ledOn)
        elif conditionIndex >= 17: #icing or etc. terrible winter weather
            if condDifference < 1:
                GPIO.output(winterLed, ledOn)
            if condDifference >= 1:
                GPIO.output(winterLed, ledOff)
            if condDifference >= 2:
                condCurTime = time.time()
    else:
        print("Condition not supported, yell at whomever wrote this program.")
        print(currentConditions)
        lcd_string("Program error", LCD_LINE_1)
        lcd_string("Unk condition", LCD_LINE_2)

#process alerts
    possibleAlerts = ["None", "Watch", "Advisory", "Warning"]
    
    if "None" in activeAlert:
        alertIndex = 0
        GPIO.output(alertLed, ledOff)
    
    if "Watch" in activeAlert:
        alertIndex = 1

    if "Advisory" in activeAlert:
        alertIndex = 2

    if "Alert" in activeAlert:
        alertIndex = 2
    
    if "Warning" in activeAlert:
        alertIndex = 3

    if alertIndex == 1:
        if alertDifference < 1:
            GPIO.output(alertLed, ledOn)
        if alertDifference >= 1:
            GPIO.output(alertLed, ledOff)
        if alertDifference >= 2:
            alertCurTime = time.time()
    if alertIndex == 2:
        GPIO.output(alertLed, ledOn)
    if alertIndex == 3:
        if alertDifference < 0.25:
            GPIO.output(alertLed, ledOn)
        if alertDifference >= 0.25:
            GPIO.output(alertLed, ledOff)
        if alertDifference >= 0.5:
            alertCurTime = time.time()

i = 0 #top string index
j = 1 #bottom string index
k = 0 #selector index

topLcdCurTime = time.time()
bottomLcdCurTime = time.time()

def processLcd():
    global i
    global j
    global k
    global topLcdCurTime
    global bottomLcdCurTime
    dataPoints = [zipMsg, alertString, tempString, windString, conditionString, dpString, humidityString, pressureString]
    topString = dataPoints[i]
    bottomString = dataPoints[j]
    newTopString = ""
    newBottomString = ""
    startIndex = 0
    endIndex = 16

    if (0 == GPIO.input(leftPin) or 0 == GPIO.input(rightPin) or 0 == GPIO.input(upPin) or 0 == GPIO.input(downPin)): #any button may be pressed here. Delay inherited from processing this function and wait times for scrolling. Ends up being about 5 seconds. 
        userSetup()

    if len(topString) > 16: #SCROLLING TEXT!!!
        while endIndex <= len(topString):
            while time.time() - topLcdCurTime >= 0.1:
                newTopString = topString[startIndex:endIndex]
                startIndex += 1
                endIndex += 1
                lcd_string(newTopString, LCD_LINE_1)
                topLcdCurTime = time.time()
        startIndex = 0
        endIndex = 16 #reset
        if i >= (len(dataPoints) - 1):
            i = 0
        else:
            i += 1
    else:
        lcd_string(topString, LCD_LINE_1)
        if i >= (len(dataPoints) - 1):
            i = 0
        else:
            i += 1

    if len(bottomString) > 16:
        while endIndex <= len(bottomString):
            while time.time() - bottomLcdCurTime >= 0.1:
                newBottomString = bottomString[startIndex:endIndex]
                startIndex += 1
                endIndex += 1
                lcd_string(newBottomString, LCD_LINE_2)
                bottomLcdCurTime = time.time()
        startIndex = 0
        endIndex = 16 #reset
        if j >= (len(dataPoints) - 1):
            j = 0
        else:
            j += 1
    else:
        lcd_string(bottomString, LCD_LINE_2)
        if j >= (len(dataPoints) - 2):
            j = 0
        else:
            j += 1
    if i == j:
        j += 1

def userSetup():
    lcd_string("Setup Program", LCD_LINE_1)
    lcd_string("* * * * * * * * * * * *", LCD_LINE_2)
    time.sleep(1)
    lcd_init()
    i = 0
    j = 1
    selections = ["Temp Units", "Speed Units", "Pressure Units", "Zip Code", "Refresh Rate", "Network Check"]  
    while True:
        selection = selections[i] 
        lcd_string(selection + " *", LCD_LINE_1)
        lcd_string(selections[j] + "", LCD_LINE_2)
        if 0 == GPIO.input(downPin): #what follows is the logic for "scrolling" through the different options
            if i >= (len(selections) - 1):
                i = 0
            else:
                i += 1
            if j >= (len(selections) - 1):
                j = 0
            else:
                j += 1
        if 0 == GPIO.input(upPin):
            if i <= 0:
                i = len(selections) - 1
            else:
                i -= 1
            if j <= 0:
                j = len(selections) - 1
            else:
                j -= 1
        if 0 == GPIO.input(rightPin): #our enter button
            lcd_init() #we're moving to the interior setup pages. Clear the lcd. Power to the main thrusters, Scotty.
            selector = "^"
            k = 0 #k will be used for the selector below
            while True:
                if 0 == GPIO.input(leftPin): #leave this menu if we press left 
                   break
                if (selection == selections[0]):
                    lcd_string("C, K, F", LCD_LINE_1)
                    lcd_string(selector, LCD_LINE_2)
                    if 0 == GPIO.input(downPin): #enter selection
                        time.sleep(0.15) #want to ensure we don't debounce
                        with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'r') as file:
                            line = file.readlines()
                            file.close()
                        line[2] = (str(k) + '\n')
                        for a, l in enumerate(line): #gets how many lines are in the file. Using 'a' is arbitrary. Will use this for rebuild the file
                            pass
                        x = 0 
                        with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'w') as file:
                            while x <= a: #we have to rebuild the whole file, so writing it back line by line with the change we want
                                file.writelines(line[x])
                                x += 1
                            file.close()
                        lcd_string("Saved!", LCD_LINE_2)
                        time.sleep(1)
                        break
                    if 0 == GPIO.input(rightPin): #moves selector to the right
                        k += 1
                        if k > 2:
                            selector = "^" #move back to starting position
                            k = 0
                        else:
                            selector = ("   " + selector) #three spaces for the increment
                            lcd_string(selector, LCD_LINE_2)

                elif (selection == selections[1]): #user sets speed unit
                    lcd_string("Km/H, MPH", LCD_LINE_1)
                    lcd_string(selector, LCD_LINE_2)
                    if 0 == GPIO.input(downPin):
                        time.sleep(0.15) 
                        with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'r') as file:
                            line = file.readlines()
                        line[0] = (str(k) + '\n') 
                        for a, l in enumerate(line):
                            pass
                        x = 0 
                        with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'w') as file:
                            while x <= a:
                                file.writelines(line[x])
                                x += 1
                            file.close()
                        lcd_string("Saved!", LCD_LINE_2)
                        time.sleep(1)
                        break #leave this menu
                    if 0 == GPIO.input(rightPin):
                        k += 1
                        if k > 1:
                            selector = "^"
                            k = 0
                        else:
                            selector = ("      " + selector) #six spaces for the increment
                            
                elif (selection == selections[2]): #user sets pressure unit
                    lcd_string("mbar, In. Hg", LCD_LINE_1)
                    lcd_string(selector, LCD_LINE_2)
                    if 0 == GPIO.input(downPin): #enter selection
                        time.sleep(0.15) 
                        with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'r') as file:
                            line = file.readlines()
                        line[1] = (str(k) + '\n')
                        for a, l in enumerate(line): 
                            pass
                        x = 0 
                        with open('/home/kpb/git/python/WeatherStation/settings.cfg', 'w') as file:
                            while x <= a: 
                                file.writelines(line[x])
                                x += 1
                        file.close()
                        lcd_string("Saved!", LCD_LINE_2)
                        time.sleep(1)
                        break #leave this menu
                    if 0 == GPIO.input(rightPin):
                        k += 1
                        if k > 1:
                            selector = "^" #move back to starting position
                            k = 0
                        else:
                            selector = ("      " + selector) #six spaces for the increment

                elif (selection == selections[3]): #user sets zip code
                    getZipcode() #runs the program then should exit the loop
                    break

                elif (selection == selections[4]):
                    setRefreshRate()
                    break

                elif (selection == selections[5]):
                    networkCheck()
                    break

        #Exiting the setup program at large. User exits by holding down any button for a second.
        curTime = time.time()
        while (0 == GPIO.input(leftPin) or 0 == GPIO.input(rightPin) or 0 == GPIO.input(upPin) or 0 == GPIO.input(downPin)): #any button may be pressed here
            elapsedTime = time.time() - curTime  
            if elapsedTime >= 1: 
                lcd_string("Exiting setup", LCD_LINE_1)
                lcd_string("* * * * * * * * * * * *", LCD_LINE_2)
                time.sleep(1)
                lcd_init()
                theProgram() #get fresh information after settings modification

curTime = time.time()
lcdCurTime = time.time()

def theProgram():
    firstRun = True
    global curTime
    global lcdCurTime
    
    while True:
        if firstRun == True:
            print("Program start")
            getSettings()
            buildUrl()
            getTime()
            getWeather()
            getAlerts()
            getTemp()
            getWind()
            getConditions()
            getDewPoint()
            getHumidity()
            getPressure()
            curTime = time.time()
            firstRun = False

        if time.time() - curTime >= refreshRate:  
            print("Refreshing Data...")
            print("##############################")
            lcd_init()
            getSettings()
            buildUrl()
            getTime()
            getWeather()
            getAlerts()
            getTemp()
            getWind()
            getConditions()
            getDewPoint()
            getHumidity()
            getPressure()        
            curTime = time.time()

        processLeds() #process leds each time this loop runs
        if (time.time() - lcdCurTime >= 5): #same thing here for the lcd
            processLcd()
            lcdCurTime = time.time()

#now the magic happens
theProgram()

#>1000 lines, holy cow!
# _____________________________________
#/ You know damn well, Kyle, that this \
#\ shouldn't have taken this long.     /
# -------------------------------------
#        \   ^__^
#         \  (oo)\_______
#            (__)\       )\/\
#                ||----w |
#                ||     ||
#
# This was a lot of fun and I learned a ton, rhyming unintentional :)
