#!/usr/bin/env python
# -----------------
# Modified 2018-09-30 to use Matt Hawkins' LCD library for I2C available
# from https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/lcd_i2c.py
#
import RPi.GPIO as GPIO
import time
import random

# Additional stuff for LCD
import smbus

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

# Set ButtonPin's mode as input with the internal pullup 

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

def buildString():
    lcd_init()
    myString = "Hello world, long string here"
    stringLength = len(myString)
    i = 0
    startIndex = 0
    endIndex = 15
    newString = []
    lcd_init()
    while endIndex <= stringLength:
        newString = myString[startIndex:endIndex]
        startIndex += 1
        endIndex += 1
        print(str(newString))
        lcd_string(newString, LCD_LINE_1)
        time.sleep(0.2)
    #while endIndex <= stringLength:
    #    lcd_string(myString, LCD_LINE_1)
    #    lcd_xy(0, startIndex)
    #    startIndex += 1
    #    endIndex += 1
#        time.sleep(2)
    #if endIndex > stringLength:
        #break #leave loop







#if stringLength > 16:
    

while True:
    buildString()
    #lcd_init()
    #lcd_string(myString, LCD_LINE_1)
    #lcd_string(" (again)", LCD_LINE_2)
    #print(str(stringLength))
    break
