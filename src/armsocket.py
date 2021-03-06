
#!/usr/bin/python
# robotic arm with voice control - python script
# author: Arthur Amarra
# created: September 2011
# Licensed under the General Public License version 3.0 or later, please see the LICENSE file for more details.
# For instructions on using this script, please read the tutorial in http://www.aonsquared.co.uk/robot_arm_tutorial_1

import pexpect
import usb.core
import time
import re
import socket

def movearm(joint,direction):
    if (direction == "UP") or (direction == "CLOSE"):
        cval = 1
    elif (direction == "DOWN") or (direction == "OPEN"):
        cval = 2
    #
    if joint == "SHOULDER":
        cbyte = (cval << 6)
    elif joint == "ELBOW":
        cbyte = (cval << 4)
    elif joint == "WRIST":
        cbyte = (cval << 2)
    elif joint == "GRIP":
        cbyte = cval
    else:
        return
    command = (cbyte, 0, 0 )
    dev.ctrl_transfer(0x40, 6, 0x100, 0, command, 1000)
    time.sleep(1)
    #stop the arm
    dev.ctrl_transfer(0x40, 6, 0x100, 0, (0,0,0), 1000)

def rotatebase(direction):
    if (direction == "RIGHT"):
        cval = 1
    elif (direction == "LEFT"):
        cval = 2
    command = (0, cval, 0 )
    dev.ctrl_transfer(0x40, 6, 0x100, 0, command, 1000)
    time.sleep(2)
    #stop the arm
    dev.ctrl_transfer(0x40, 6, 0x100, 0, (0,0,0), 1000)

def ctrl_light(light_comm):
    if (light_comm == "ON"):
        cval = 1
    elif (light_comm == "OFF"):
        cval = 0
    command = (0, 0, cval )
    dev.ctrl_transfer(0x40, 6, 0x100, 0, command, 1000)


if __name__ == "__main__":

    dev = usb.core.find(idVendor=0x1267, idProduct=0x0000)

    #exit if device not found
    if dev is None:
        raise ValueError('Can\'t find robot arm!')

    #this arm should just have one configuration...
    dev.set_configuration()

    HOST = ''                 # Symbolic name meaning the local host
    PORT = 50007              # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    while 1:
      print "Listening"
      s.listen(1)
      conn, addr = s.accept()
      print 'Connected by', addr

      while 1:
        data = conn.recv(1)
        if not data: break

        c = data[0]
        print "Received ",ord(c)," ",c

        if c == "l": rotatebase("LEFT")
        if c == "r": rotatebase("RIGHT")
        if c == "u": movearm("SHOULDER","UP")
        if c == "d": movearm("SHOULDER","DOWN")
        if c == "e": movearm("ELBOW","UP")
        if c == "f": movearm("ELBOW","DOWN")
        if c == "w": movearm("WRIST","UP")
        if c == "x": movearm("WRIST","DOWN")
        if c == "o": movearm("GRIP","OPEN")
        if c == "g": movearm("GRIP","CLOSE")
        if ord(c) == 13:
          print "Closing socket"
          conn.close()
          break

