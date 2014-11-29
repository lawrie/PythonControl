#!/usr/bin/env python

import RPi.GPIO as GPIO
import socket
from subprocess import call
from plugins.cameraled import CameraLED
from parser.parser import Parser

# Accept requests from any IP address on port 50000
TCP_IP = '0.0.0.0'
TCP_PORT = 50000
BUFFER_SIZE = 4096

# Create socket and bind it to TCP address &amp; port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))

led = CameraLED()
parser = Parser();

# Infinite loop
while 1:
    # Listen for a connection
    s.listen(1)
    # Connection found. Accept connection
    conn, addr = s.accept()

    data = conn.recv(BUFFER_SIZE).rstrip()
    tokens = parser.parse(data);
    #print tokens
    l = len(tokens)
    if l > 0 and tokens[0]  == "led":
        if l > 1 and tokens[1] == "on":
          # print "Turn LED on"
          led.turnOn()
        elif l > 1 and tokens[1] == "off":
          # print "Turn LED off"
          led.turnOff()
    conn.send(data)
    conn.close()
