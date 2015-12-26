#!/usr/bin/env python

import paho.mqtt.client as mqtt
import time
import grovepi
import smbus
import RPi.GPIO as GPIO
from datetime import datetime
from mpd import MPDClient
import urllib2
import os
import logging
import logging.handlers
import sys
import socket
from subprocess import call

LOG_FILENAME = "/tmp/radio.log"
LOG_LEVEL = logging.INFO

# LCD has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

CLOCK_DISPLAY = 0
RADIO_DISPLAY = 1
MENU_DISPLAY = 2
SENSOR_DISPLAY = 3
ALARM_DISPLAY = 4
MAX_DISPLAY = 4

# Submenus
RADIO_MENU = 0
OFF_MENU = 1
VOLUME_MENU = 2
ALARM_MENU = 3
SHUTDOWN_MENU = 4
REBOOT_MENU = 5
MAX_MENU = 5

# Digital pins
BUZZER_PIN = 6
BUTTON1_PIN = 3
BUTTON2_PIN = 2

# Analog pins
TEMPERATURE_PIN = 0
SOUND_PIN = 1
LIGHT_PIN = 2

SLEEP_PERIOD = 1
TEMPERATURE_TOPIC = '/house/rooms/second-floor/master-bedroom/temperature'
LIGHT_TOPIC = '/house/rooms/second-floor/master-bedroom/light-level'
PUBLISH_PERIODS = 10

color = 0x770077

# Working data
display = 0
subMenu = 0
buzzing = False
alarmSet = False
backLight = True
period = PUBLISH_PERIODS
menu = False
radio = False
playlist = 0
playlists = None
subMenuSelected = False
playing = False
volume = 8
title = None
titleScroll = 0
oldSong = None
hours=0
minutes=0
alarmDay = False
connected = False

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)

# Set pin modes
grovepi.pinMode(BUZZER_PIN ,"OUTPUT")

# use the bus that matches your raspi version
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(c):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,(c >> 16) & 0xff)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,(c >> 8) & 0xff)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,c & 0xff)

# send command to display (no need for external use)
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

# set display text \n for second line(or auto wrap)
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("MQTT connected with result code "+str(rc))
    connected = True

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
def on_disconnect(client, userdata, rc):
    connected = False
    if rc != 0:
        print("Unexpected disconnection.")

def buzz():
    grovepi.digitalWrite(BUZZER_PIN,1)
    time.sleep(1)
    grovepi.digitalWrite(BUZZER_PIN,0)
    
def internet_on():
    try:
        urllib2.urlopen('http://192.168.0.101',timeout=1).close()
        return True
    except urllib2.URLError as err: pass
    return False
    
def read_buttons():
	startTime = datetime.now()
	while (datetime.now() - startTime).seconds < 1:
		button1 = grovepi.digitalRead(BUTTON1_PIN)
		if button1:
			print "button 1 down"
			buttonTime = datetime.now()
			while grovepi.digitalRead(BUTTON1_PIN) and (datetime.now() - buttonTime).seconds < 1:
				time.sleep(.001)
			downTime = (datetime.now() - buttonTime).microseconds
			if  downTime > 120000:
				print "Returning 1, down time " + str(downTime)
				return 1
			else:
				print "Phantom press, down time " + str(downTime)
		button2 = grovepi.digitalRead(BUTTON2_PIN)
		if button2:
			print "button 2 down"
			buttonTime = datetime.now()
			while grovepi.digitalRead(BUTTON2_PIN) and (datetime.now() - buttonTime).seconds < 1:
				time.sleep(.001)
			downTime = (datetime.now() - buttonTime).microseconds
			if downTime > 120000:
				print "Returning 2, down time " + str(downTime)
				return 2
			else:
				print "Phantom press, down time " + str(downTime)
	return 0 
     		
# Connect to MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.loop_start()

try:
	client.connect("192.168.0.101", 1883, 60)
	
except socket.error:
	print "Failed to connect to mqtt"	

while True:
    try:
	    mpc = MPDClient()
	    mpc.timeout = 10

	    mpc.connect("localhost", 6600)
	    mpc.setvol(volume*10)
	    playlists = mpc.listplaylists()
	    print playlists
	    break
    except socket.error:
	    print "Failed to connect to mpd"
	    setText("mpc failure")
	    button = 0
	    while not button:
	        button = read_buttons()
	    setText("Retrying ...")  

# Main loop
while True:
    try:
        # Process buttons
        button = read_buttons()
        
        if button:
        	oldSong = None
                 
        # Scroll through  displays or menus, or submenu items         
        if button == 1:
            #print 'Button 1 pressed'
            #call(["espeak","-s140 -ven+18 -z","Button 1 pressed"])
            
            if not(menu):
                display += 1
                if display > MAX_DISPLAY:
                    display = 0
            else:
                if subMenuSelected:
                    if subMenu == VOLUME_MENU:
                        volume += 1
                        if volume == 11:
                            volume = 0
                    elif subMenu == RADIO_MENU:
                        playlist += 1
                        if playlists != None and playlist == len(playlists):
                            playlist = 0
                    elif subMenu == ALARM_MENU:
                        hours += 1
                        if hours == 24:
                            hours = 0
                else:
                    subMenu += 1
                    if subMenu > MAX_MENU:
                        subMenu = 0
        
        # select menu or submenu item, or turn backlight on/off        
        if button == 2:
            if buzzing:
                buzzing = False
            elif subMenuSelected:
                if subMenu == RADIO_MENU:
                    if playlists != None:
                        try:
                            setText("clear")
                            mpc.clear()
                            setText("load")
                            mpc.load(playlists[playlist]['playlist'])
                            setText("play")
                            mpc.play()
                            playing = True
                        except:
                            e = sys.exc_info()[0]
                            print "Exception in play ", e
                    display = RADIO_DISPLAY
                elif subMenu == VOLUME_MENU:
                    mpc.setvol(volume*10)
                    display = RADIO_DISPLAY
                elif subMenu == ALARM_MENU:
                    alarmSet = True
                    display = ALARM_DISPLAY
                    timeNow = datetime.now()
                    alarmDay =  (hours > timeNow.hour or (hours == timeNow.hour and minutes > timeNow.minute))              
                subMenuSelected = False
                menu = False
            elif menu:
                if subMenu == RADIO_MENU:
                    playList = 0
                if subMenu == OFF_MENU:
                    mpc.stop()
                    playing = False
                    menu = False
                    display = CLOCK_DISPLAY
                else:
                    subMenuSelected = True
            elif display != MENU_DISPLAY:
                backLight = not(backLight)
            else:
                menu = True
                subMenu = 0
                subMenuSelected = False

        # Process sensor data
        period += 1
        #print "Period is " + str(period) + " of " + str(PUBLISH_PERIODS)
        if period >= PUBLISH_PERIODS:
	        # Get sensor data
	        period = 0        
	        temp = grovepi.temp(TEMPERATURE_PIN,'1.1')
	        #print "  Temp =", temp
	        sound = grovepi.analogRead(SOUND_PIN)
	        #print "  Sound =", sound
	        light = grovepi.analogRead(LIGHT_PIN)
	        #print "  Light =", light
	                         
	        # Check if Internet is available
	        print "Internet on " + str(internet_on())
	        
	        os.system("./netcheck")
	        
	        # Publish sensor data
	        client.publish(TEMPERATURE_TOPIC,str(temp*10));
	        client.publish(LIGHT_TOPIC,str(light));

        #print "Backlight is " + str(backLight)
        # Set the backlight
        if backLight:
            setRGB(color)
        else:
            setRGB(0)
            
        #print "Display is " + str(display)
        # Display data
        if menu:
            #print "In menu " + str(subMenu)
            if subMenu == VOLUME_MENU:
                if subMenuSelected:
                    setText(str(volume))
                else:
                    setText("Set volume")
            elif subMenu == OFF_MENU:
                setText("Turn radio off")
            elif subMenu == RADIO_MENU:
                if subMenuSelected:
                    if playlists != None:
                        setText(playlists[playlist]["playlist"])
                else:
                    setText("Choose radio\nstation") 
            elif subMenu == ALARM_MENU:
                if subMenuSelected:
                    setText(str(hours))
                else:
                    setText("Set alarm")
            elif subMenu == SHUTDOWN_MENU:
                if subMenuSelected:
                    setText("Shutting down")
                    setRGB(0)
                    os.system("sudo poweroff")
                else:
                    setText("Shutdown the rPi")
            elif subMenu == REBOOT_MENU:
                if subMenuSelected:
                    setText("Rebooting")
                    setRGB(0)
                    os.system("sudo reboot")
                else:
                    setText("Reboot the rPi")                    
        else:
	        if display == CLOCK_DISPLAY:
	            setText(datetime.now().strftime("%a %d %b %Y") + "\n" + datetime.now().strftime("%I:%M %p"))
	        elif display == SENSOR_DISPLAY:
	            setText("T: {:.2f}".format(temp) + " L: " + str(light) + "\nS: " + str(sound)) 
	        elif display == MENU_DISPLAY:
	            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); 
	            s.connect(('8.8.8.8', 80)); 
	            ip = s.getsockname()[0]; 
	            s.close()
	            setText("Main Menu\n" + ip)
	        elif display == RADIO_DISPLAY:
	            if playing:
	                currentSong = mpc.currentsong()
	                #print currentSong
	                if currentSong != oldSong:
	                    title = mpc.currentsong()['title'] if 'title' in mpc.currentsong() else mpc.currentsong()['name'] if 'name' in mpc.currentsong() else "Unknown song"
	                    print "Playing " + title
	                    setText(title)
	                    titleScroll = len(title) - 32
	                    ts = 0
	                elif titleScroll > 0:
	                    ts += 1
	                    if ts > titleScroll:
	                        ts = 0
	                    setText(title[ts:])
	                oldSong = currentSong
	            else:
	                setText("Radio not\nplaying")
	        elif display == ALARM_DISPLAY:
	            if alarmSet:
	                setText("Alarm: " + str(hours) + ":" + str(minutes))
	            else:
	                setText("Alarm not set\nconnected: " + str(connected))
            
        # Deal with alarm
        if (buzzing):
            buzz() 
            
        timeNow = datetime.now()
        
        if alarmSet and not(alarmDay):
            if timeNow.hour == 0:
                alarmDay = True
        
        if alarmSet and alarmDay and timeNow.hour >= hours and timeNow.minute >= minutes:
            buzzing = True
            alarmSet = False

    except KeyboardInterrupt:
        break
    except IOError:
        print "I/O Error"
    except socket.error:
        print "Socket test"