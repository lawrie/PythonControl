
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

def remove_tags(data):
    p = re.compile(r'<[^<]*?>')
    return p.sub('', data)

def process_sentence(sentence_text):
        str1 = remove_tags(sentence_text)
        str2 = str1.replace('sentence1: ','')
        joints = ['ELBOW', 'SHOULDER', 'WRIST', 'GRIP']
        transcribed = str2.split()
        if transcribed[0] in joints:
                movearm(transcribed[0],transcribed[1])
        elif transcribed[0] == "LIGHT":
                ctrl_light(transcribed[1])
        elif transcribed[0] == "BASE":
                rotatebase(transcribed[1])

def get_confidence(out_text):
    linearray = out_text.split("\n")
    for line in linearray:
        if line.find('sentence1') != -1:
            sentence1 = line
        elif line.find('cmscore1') != -1:
            cmscore1 = line
        elif line.find('score1') != -1:
            score1 = line
    cmscore_array = cmscore1.split()
    err_flag = False
    for score in cmscore_array:
        try:
            ns = float(score)
        except ValueError:
            continue
        if (ns < 0.999):
            err_flag = True
            print "confidence error:", ns, ":", sentence1
    score1_val = float(score1.split()[1])
    if score1_val < -13000:
        err_flag = True
        print "score1 error:", score1_val, sentence1
    if (not err_flag):
        print sentence1
        print score1
        #pass sentence1 to controller functions
        process_sentence(sentence1)
    else:
        pass


def process_julius(out_text):
    match_res = re.match(r'(.*)sentence1(\.*)', out_text, re.S)
    if match_res:
        get_confidence(out_text)
    else:
                pass


if __name__ == "__main__":

    dev = usb.core.find(idVendor=0x1267, idProduct=0x0000)

    #exit if device not found
    if dev is None:
        raise ValueError('Can\'t find robot arm!')

    #this arm should just have one configuration...
    dev.set_configuration()

    child = pexpect.spawn ('julius -input mic -C julian.jconf')

    while True:
        try:
            child.expect('please speak')
            process_julius(child.before)
        except KeyboardInterrupt:
            child.close(force=True)
            break
