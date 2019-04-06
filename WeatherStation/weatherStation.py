#Title: Raspberry Pi Weather Station
#Purpose: COMP430 Final Project
#Author: Kyle Belouin, external libraries used

import datetime
import time
import urllib.request
import smbus
import subprocess
import os

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

##GPIO.setwarnings(False)
##GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by standard marking
##GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
##GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to turn off led

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
  #        0 for command

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
        print("Houston? We have a problem. Can't open webpage...")
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
    unit = units[(int((settings.readline())))] #line 1 in settings.cfg corresponds to units
    pressureUnit = pressureUnits[(int((settings.readline())))] #line 2 for pressureUnits  
    tempUnit = tempUnits[(int((settings.readline())))] #line 3 for tempUnits
    zipcode = str(settings.readline()) #line 4 holds zipcode 
    return unit
    return pressureUnit
    return tempUnit
    return zipcode
    return settings
    settings.close()#we're done here, close the file

def getZipcode():
    while True:
        global promptZip 
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
            return promptZip
            break

def buildUrl(): #this is so janky
    searchUrl = ("https://search.yahoo.com/search?p=" + str(promptZip) + "+weather&fr=uh3_magweather_web_gs&fr2=p%3Aweather%2Cm%3Asb") 
    searchWebpage = str(webRead(searchUrl)) #getting the webpage
    searchWebpageIndex = searchWebpage.find('compText mt-10 mb-10 ml-10')#seeking for a constant tag
    searchWebpageIndex = searchWebpage.find('href', searchWebpageIndex)#further seeking
    searchWebpageIndex = searchWebpageIndex + 6 #found we needed to 6 chars in
    endSearchWebpageIndex = (searchWebpage.find('"', searchWebpageIndex) - 1) #link ends at a ". 
    urlList = []
    difference = (endSearchWebpageIndex - searchWebpageIndex)
    i = 0
    while i <= difference:
        urlList.append(searchWebpage[searchWebpageIndex + i])
        i += 1 
    global url
    url = ''.join(map(str,urlList))
    return url

#Grabbing web page for Manchester,NH
def getWeather():
    webpage = (str(webRead(url)))
    #Save to file
    file = open('webpageout.txt', 'w')
    file.write(str(webpage))
    file.close()

    #Finding temperature
    tempIndex = webpage.find(('class="Va(t)"'))
    temp = []
    i = 32 #found the temperature value is at +32 characters in from the search query
    while i <= 33: #this pulls the values from the long string, enters then into an array...
        temp.append (webpage[tempIndex + i])
        i += 1
    tempInt = int((temp[0] + temp[1])) #...then converts those two numbers into integers.
    if (tempUnit == tempUnits[0]):#Celcius
        tempInt = round(((tempInt - 32) * (5/9)), 1)
        print("Temperature: " + (str(tempInt)) + "°C")
    elif (tempUnit == tempUnits[1]):#Kelvin...for the nerds.
        tempInt = round(((tempInt - 32) * (5/9) + 273.15), 2)
        print("Temperature: " + (str(tempInt)) + "°K")
    else: #Fahrenheit
        print("Temperature: " + (str(tempInt)) + "°F")

  #Finding windspeed
    windIndex = webpage.find(('<span data-reactid="457">'))
    wind = []
    i = 24
    while i < 27:
        wind.append (webpage[windIndex + i])
        i += 1
    if (wind[0] == ">"): #this accounts for when the wind is <10, putting a zero in instead of the close tag
        wind[0] = "0"
        windInt = int((wind[0] + wind[1] + wind[2]))
    if unit == "metric":
        windInt = round((windInt * 1.60934), 0)
        speedUnit = "Km/h"
    else:
        speedUnit = "MPH"
    #Finding wind direction
    windDirIndex = webpage.find(('<!-- react-text: 458 -->'))
    windDir = []
    i = 26
    while i < 29:
        windDir.append (webpage[windDirIndex + i])
        i += 1
      
    print("Windspeed: " + (str(windInt)) + speedUnit + " " + (windDir[0]))
    
    #Finding conditions
    conditionIndex = webpage.find(('description Va(m)'))
    conditionIndex = webpage.find(('data-reactid="26"'), conditionIndex)
    conditionIndex = webpage.find('>', conditionIndex) + 1
    endIndex = webpage.find('<', conditionIndex) - 1
    webpageConditions = []
    stringLength = endIndex - conditionIndex
    i = 0
    while i <= stringLength:
        webpageConditions.append (webpage[conditionIndex + i])
        i += 1
    currentConditions = ''.join(map(str,webpageConditions))#turning the webpageConditions list into string
    print("Conditions: " + currentConditions)

    #Finding humidity
    humidityIndex = webpage.find(('data-reactid="480"'))
    humidity = []
    i = 19
    while i <= 20:
        humidity.append (webpage[humidityIndex + i])
        i += 1
    humidityPercent = int((humidity[0] + humidity[1]))
    print("Humidity: " + (str(humidityPercent) + "%"))

    #Finding barometric pressure
    pressureIndex = webpage.find(('data-reactid="462"'))
    pressure = []
    i = 19
    while i <= 22:
        pressure.append (webpage[pressureIndex + i])
        i += 1
    pressure = ''.join(map(str,pressure)) #turning the list into a string...
    pressure = float(pressure) #...then to an float
    if pressureUnit == pressureUnits[0]:
        pressure = round((pressure * 33.8639), 1)
        print("Barometric pressure: " + (str(pressure)) + " mbar")
    else:
        print("Barometric pressure: " + (str(pressure)) + " in. Hg")
    
curTime = time.time()
firstRun = 0

while True:
  if (firstRun == 0):
    getSettings()#perhaps the user has changed the units since last run
    getZipcode()
    getTime()
    buildUrl()
    getWeather()
    firstRun = 1
    
  if (time.time()) - curTime >= 60:  
    print("Refreshing Data...")
    print("##############################")
    getSettings()
    getTime()
    getWeather()
    curTime = time.time()
  
