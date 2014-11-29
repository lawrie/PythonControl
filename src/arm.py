
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

    rotatebase("LEFT")
    rotatebase("RIGHT")
    movearm("SHOULDER","UP")

    movearm("GRIP","OPEN")
    movearm("SHOULDER","DOWN")
    movearm("SHOULDER","DOWN")
    movearm("SHOULDER","DOWN")
    movearm("GRIP","CLOSE")
    movearm("GRIP","CLOSE")
    movearm("SHOULDER","UP")
    movearm("SHOULDER","UP")
    movearm("SHOULDER","UP")
    movearm("GRIP","OPEN")

