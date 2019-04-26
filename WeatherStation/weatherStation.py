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
    # Get a handle to the URL object
    try:
        # print("Trying to open webpage...")
        h = urllib.request.urlopen(URL)
        # print("Opened webpage... ")
        response = h.read()
        #print(len(response)," chars in the response")
    except:
        print("Page failed to load. Ensure you didn't enter an invalid zip code or check the network.")
        response = ""

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
def getSettings(): #will have to redo as a 'getSettings' file
    global settings 
    settings = open('settings.cfg', 'r')
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
    while True: 
        promptZip = input("Enter in a 5-Digit Zip Code: ")
        type (promptZip)
        if (len(promptZip) != 5):
            print("Invalid zipcode entered. Please try again.")
        else: #read the file to get # of lines, then write to our designated line
            with open('settings.cfg', 'r') as file: 
                line = file.readlines()          
            line[3] = str(promptZip)
            with open('settings.cfg', 'w') as file:
                file.writelines(line)
            zipcode = promptZip    
            return zipcode
            break

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
        direction = ''.join(map(str,windDir)) #string joining discovered here https://www.programiz.com/python-programming/methods/string/join
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
        pressure = round((pressure * 33.8639), 1)
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

#print(alertString)

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
    if tempUnit == "C":
        if tempInt < 4.5:     
            if difference < 3:
                GPIO.output(tempLed, ledOn)
            if difference >= 3:
                GPIO.output(tempLed, ledOff)
            if difference >= 6:
                ledCurTime = time.time()
         
        if tempInt > 4.5 < 12.8:
            if difference < 2:
                GPIO.output(tempLed, ledOn)
            if difference >= 2:
                GPIO.output(tempLed, ledOff)
            if difference >= 4:
                ledCurTime = time.time()

        if tempInt > 12.8 < 21.1:
            GPIO.output(tempLed, ledOn)

        if tempInt > 21.1:
            if difference < 1:
                GPIO.output(tempLed, ledOn)
            if difference >= 1:
                GPIO.output(tempLed, ledOff)
            if difference >= 2:
                #global ledCurTime
                ledCurTime = time.time()

    if tempUnit == "F":
        if tempInt < 40:
            if difference < 3:
                GPIO.output(tempLed, ledOn)
            if difference >= 3:
                GPIO.output(tempLed, ledOff)
            if difference >= 6: 
                ledCurTime = time.time()

        if tempInt > 40 < 55:
            if difference < 2:
                GPIO.output(tempLed, ledOn)
            if difference >= 2:
                GPIO.output(tempLed, ledOff)
            if difference >= 4:
                ledCurTime = time.time()
        
        if tempInt > 55 < 70:
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

        if tempInt > 277.594 < 285.928:
            if difference < 2:
                GPIO.output(tempLed, ledOn)
            if difference >= 2:
                GPIO.output(tempLed, ledOff)
            if difference >= 4:
                ledCurTime = time.time()
        
        if tempInt > 285.928 < 294.261:
            GPIO.output(tempLed, ledOn)
        
        if tempInt > 294.261:
            if difference < 1:
                GPIO.output(tempLed, ledOn)
            if difference >= 1:
                GPIO.output(tempLed, ledOff)
            if difference >= 2:
                ledCurTime = time.time()

#process for conditions incl winter
    possibleConditions = ["Clear", "Sunny", "Mostly Sunny", "Partly Cloudy", "Fair", "Cloudy", "Mostly Cloudy", "Overcast", "Showers", "Light Rain", "Rain", "Rain Shower", "Heavy Rain", "Thunderstorm", "Light Snow", "Snow Shower", "Snow", "Sleet", "Freezing Rain", "Ice"]

    if currentConditions in possibleConditions:
        conditionIndex = possibleConditions.index(currentConditions)
        if conditionIndex <= 4: #sunny, etc
            GPIO.output(conditionLed, ledOn)
        elif conditionIndex >= 5 <= 7: #cloudy
            if condDifference < 1:
                GPIO.output(conditionLed, ledOn)
            if condDifference >= 1:
                GPIO.output(conditionLed, ledOff)
            if condDifference >= 2:
                condCurTime = time.time()
        elif conditionIndex >= 8 <= 12: #rain of some sort 
            if condDifference < 2:       
                GPIO.output(conditionLed, ledOn)
            if condDifference >= 2:    
                GPIO.output(conditionLed, ledOff)
            if condDifference >= 4:          
                condCurTime = time.time()
        elif conditionIndex == 13: #water is falling from the sky, likely at a high rate and with electrostaic discharges
           if condDifference < 3:
               GPIO.output(conditionLed, ledOn)
           if condDifference >= 3:
               GPIO.output(conditionLed, ledOff)
           if condDifference >= 6:
               condCurTime = time.time()
        elif conditionIndex >= 14 <= 16: #snowing!
            GPIO.output(winterLed, ledOn)
        #else:
        #    GPIO.output(winterLed, ledOff)
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
        lcd_string("", LCD_LINE_2)

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

lcd_init()
#print(alertString)

i = 0
j = 1
k = 0
l = 15
topLcdCurTime = time.time()
bottomLcdCurTime = time.time()

def processLcd():
    global i
    global j
    global k
    global l
    global topLcdCurTime
    global bottomLcdCurTime
    dataPoints = [zipMsg, alertString, tempString, windString, conditionString, dpString, humidityString, pressureString]
    topString = dataPoints[i]
    bottomString = dataPoints[j]
    newTopString = ""
    newBottomString = ""
    startIndex = 0
    endIndex = 16

    if (0 == GPIO.input(leftPin) or 0 == GPIO.input(rightPin) or 0 == GPIO.input(upPin) or 0 == GPIO.input(downPin)): #any button may be pressed here
        userSetup()

    if len(topString) > 16:
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
        #if j >= len(bottomString):
        #    j = 0
    if i == j:
        j += 1

def userSetup():
    lcd_string("Setup Program", LCD_LINE_1)
    lcd_string("* * * * * * * * * * * *", LCD_LINE_2)
    time.sleep(1)
    lcd_init()
    i = 0
    j = 1
    selections = ["Temp Units", "Speed Units", "Pressure Units", "Zip Code", "Refresh Rate"]  
    while True:
        selection = selections[i] 
        lcd_string(selection + " *", LCD_LINE_1)
        lcd_string(selections[j] + "", LCD_LINE_2)
        if (0 == GPIO.input(downPin)): #what follows is the logic for "scrolling" through the different options
            if i >= (len(selections) - 1):
                i = 0
            else:
                i += 1
            if j >= (len(selections) - 1):
                j = 0
            else:
                j += 1
        if (0 == GPIO.input(upPin)):
            if i <= 0:
                i = len(selections) - 1
            else:
                i -= 1
            if j <= 0:
                j = len(selections) - 1
            else:
                j -= 1
        if (0 == GPIO.input(rightPin)):
            lcd_init() #we're moving to the interior setup pages. Clear the lcd
            selector = "*"
            k = 0 #k will be used for the selector below
            while True:
                if 0 == GPIO.input(leftPin): #leave this menu if we press left 
                   break
                if (selection == selections[0]):
                    lcd_string("C, K, F", LCD_LINE_1)
                    lcd_string(selector, LCD_LINE_2)
                    if 0 == GPIO.input(downPin): #enter selection
                        time.sleep(0.15) #want to ensure we don't debounce
                        with open('settings.cfg', 'r') as file:
                            line = file.readlines()
                        line[2] = (str(k) + '\n')
                        for a, l in enumerate(line): #gets how many lines are in the file. Using 'a' is arbitrary
                            pass
                        x = 0 
                        with open('settings.cfg', 'w') as file:
                            while x <= a: #we have to rebuild the whole file, so writing it back line by line with the change we want
                                file.writelines(line[x])
                                x += 1
                        file.close()
                        lcd_string("Saved!", LCD_LINE_2)
                        time.sleep(1)
                        break
                    if (0 == GPIO.input(rightPin)):
                        k += 1
                        if k > 2:
                            selector = "*" #move back to starting position
                            k = 0
                        else:
                            selector = ("   " + selector) #three spaces for the increment
                            lcd_string(selector, LCD_LINE_2)

                elif (selection == selections[1]): #user sets speed unit
                    lcd_string("Km/H, MPH", LCD_LINE_1)
                    lcd_string(selector, LCD_LINE_2)
                    if 0 == GPIO.input(downPin): #enter selection
                        time.sleep(0.15) #want to ensure we don't debounce
                        with open('settings.cfg', 'r') as file:
                            line = file.readlines()
                        line[0] = (str(k) + '\n') 
                        for a, l in enumerate(line): #gets how many lines are in the file. Using 'a' is arbitrary
                            pass
                        x = 0 
                        with open('settings.cfg', 'w') as file:
                            while x <= a: #we have to rebuild the whole file, so writing it back line by line with the change we want
                                file.writelines(line[x])
                                x += 1
                        file.close()
                        lcd_string("Saved!", LCD_LINE_2)
                        time.sleep(1)
                        break #leave this menu
                    if (0 == GPIO.input(rightPin)):
                        k += 1
                        if k > 1:
                            selector = "*" #move back to starting position
                            k = 0
                        else:
                            selector = ("       " + selector) #seven spaces for the increment
                elif (selection == selections[2]): #user sets pressure unit
                    lcd_string("mbar, In. Hg", LCD_LINE_1)
                    lcd_string(selector, LCD_LINE_2)
                    if 0 == GPIO.input(downPin): #enter selection
                        time.sleep(0.15) #want to ensure we don't debounce
                        with open('settings.cfg', 'r') as file:
                            line = file.readlines()
                        line[1] = (str(k) + '\n')
                        for a, l in enumerate(line): #gets how many lines are in the file. Using 'a' is arbitrary
                            pass
                        x = 0 
                        with open('settings.cfg', 'w') as file:
                            while x <= a: #we have to rebuild the whole file, so writing it back line by line with the change we want
                                file.writelines(line[x])
                                x += 1
                        file.close()
                        lcd_string("Saved!", LCD_LINE_2)
                        time.sleep(1)
                        break #leave this menu
                    if (0 == GPIO.input(rightPin)):
                        k += 1
                        if k > 1:
                            selector = "*" #move back to starting position
                            k = 0
                        else:
                            selector = ("      " + selector) #six spaces for the increment
                elif (selection == selections[3]): #user sets zip code
                    with open('settings.cfg', 'r') as file:
                        line = file.readlines()
                        zipcode = (line[3])
                        zipcode = zipcode.replace('\n' , "") #there's a newline that has to be dropped
                        zipcode = int(zipcode)
                    lcd_string(str(zipcode).zfill(5), LCD_LINE_1) #zfill to ensure we always display 5 characters, despite there being a zero
                    lcd_string(selector, LCD_LINE_2)
                    
                    if 0 == GPIO.input(upPin):
                        if k == 0:
                            zipcode = zipcode + 10000
                        if k == 1:
                            zipcode = zipcode + 1000
                        if k == 2:
                            zipcode = zipcode + 100
                        if k == 3:
                            zipcode = zipcode + 10
                        if k == 4:
                            zipcode = zipcode + 1
                    if 0 == GPIO.input(downPin): #enter selection
                        time.sleep(0.15) #want to ensure we don't debounce  
                        line[3] = (str(k) + '\n')
                        for a, l in enumerate(line): #gets how many lines are in the file. Using 'a' is arbitrary
                            pass
                        x = 0 
                        with open('settings.cfg', 'w') as file:
                            while x <= a: #we have to rebuild the whole file, so writing it back line by line with the change we want
                                file.writelines(line[x])
                                x += 1
                        file.close()
                        lcd_string("Saved!", LCD_LINE_2)
                        time.sleep(1)
                        break #leave this menu
                    if (0 == GPIO.input(rightPin)):
                        k += 1
                        if k > 5:
                            selector = "*" #move back to starting position
                            k = 0
                        else:
                            selector = (" " + selector) #six spaces for the increment

                else:
                    break

        curTime = time.time()
        while (0 == GPIO.input(leftPin) or 0 == GPIO.input(rightPin) or 0 == GPIO.input(upPin) or 0 == GPIO.input(downPin)): #any button may be pressed here
            elapsedTime = time.time() - curTime  
            if elapsedTime >= 2: 
                lcd_string("Exiting setup", LCD_LINE_1)
                lcd_string("* * * * * * * * * * * *", LCD_LINE_2)
                time.sleep(1)
                lcd_init()
                return

firstRun = 0
curTime = time.time()
lcdCurTime = time.time()

while True:     
    if firstRun == 0:
        firstRun += 1
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

    if time.time() - curTime >= refreshRate:  
        print("Refreshing Data...")
        print("##############################")
        lcd_init()
        lcd_string("Refreshing Data", LCD_LINE_1)
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
