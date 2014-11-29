
import serial
import time
import usb.core

def getch():
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

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


    dev = usb.core.find(idVendor=0x1267, idProduct=0x0000)

    #exit if device not found
    if dev is None:
        raise ValueError('Can\'t find robot arm!')

    #this arm should just have one configuration...
    dev.set_configuration()

def baud(hz):
  ser.write(chr(129) + chr(hz))

def forward():
  ser.write(chr(137) + chr(speed >> 8 & 0xff) + chr(speed & 0xff) + chr(0x80) + chr(0))

def backward():
  ser.write(chr(137) + chr(-speed >> 8 & 0xff) + chr(-speed & 0xff) + chr(0x80) + chr(0))

def stop():
  ser.write(chr(137) + chr(0) + chr(0) + chr(0) + chr(0))

def arc(r):
  ser.write(chr(137) + chr(speed >> 8 & 0xff) + chr(speed & 0xff) + chr(radius >> 8 & 0xff) + chr(radius &0xff))

def spinleft():
  ser.write(chr(137) + chr(speed >> 8 & 0xff) + chr(speed & 0xff) + chr(0) + chr(1))

def spinright():
  ser.write(chr(137) + chr(speed >> 8 & 0xff) + chr(speed & 0xff) + chr(0xff) + chr(0xff))

def motors(m=7):
  ser.write(chr(138) + chr(m))

def dock():
  ser.write(chr(143))

def control():
  ser.write(chr(130))

def start():
  ser.write(chr(128))

def sleep():
  ser.write(chr(133))

def safe():
  ser.write(chr(131))

def full():
  ser.write(chr(132))

def spot():
  ser.write(chr(134))

def max():
  ser.write(chr(136))

def clean():
  ser.write(chr(135))

def updatesensors():
  ser.write(chr(142) + chr(1))
  time.sleep(0.5)
  sensors = ser.read(10)
  while len(sensors) == 10:
    temp = ser.read(10)
    if len(temp) == 0:
      break
    sensors = temp
  return sensors

def sense():
  sensors = updatesensors()
  if len(sensors) == 10:
    print ord(sensors[0])

def step():
  sensors = updatesensors()
  if len(sensors) == 10:
    #print 'sensor 0 = ',ord(sensors[0])
    if ord(sensors[0]) & 0x01:
      #print 'spin left'
      spinleft()
      motors()
      time.sleep(1)
    elif ord(sensors[0]) & 0x02:
      #print 'spin right'
      spinright()
      time.sleep(1)
    else:
      forward()
  else:
     print 'No sensor value ',len(sensors)

def help():
  print 'arrow keys to move robot, s to stop'
  print 'u and d for shoulder up and down'
  print 'e and f for elbow up and down'
  print 'w and x for wrist left and right'
  print 'g and o for grabber close and open'
  print 'm and n for motors on and off'
  print 'p for spot, h for dock, c for control'

#main
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
speed = 200

dev = usb.core.find(idVendor=0x1267, idProduct=0x0000)

#exit if device not found
if dev is None:
  raise ValueError('Can\'t find robot arm!')

#this arm should just have one configuration...
dev.set_configuration()

while 1:
  sensors = updatesensors()
  k = getch()

  if k == "l": rotatebase("LEFT")
  elif k == "r": rotatebase("RIGHT")
  elif k == "u": movearm("SHOULDER","UP")
  elif k == "d": movearm("SHOULDER","DOWN")
  elif k == "e": movearm("ELBOW","UP")
  elif k == "f": movearm("ELBOW","DOWN")
  elif k == "w": movearm("WRIST","UP")
  elif k == "x": movearm("WRIST","DOWN")
  elif k == "o": movearm("GRIP","OPEN")
  elif k == "g": movearm("GRIP","CLOSE")
  elif k == chr(3) or k == 'q': break
  elif k == "?": help();
  elif k == 's': stop()
  elif k == 'm': motors()
  elif k == 'n': motors(0)
  elif k == 'p': spot()
  elif k == 'c': control()
  elif k == 'h': dock()
  elif k == 'z': sense()
  elif ord(k) == 27:
    dummy = getch()
    k = getch()
    if ord(k) == 65: forward()
    elif ord(k) == 66: backward()
    elif ord(k) == 68: spinleft()
    elif ord(k) == 67: spinright()
    else:
      print 'Unrecognized special key ',ord(k)
  else:
    print 'Unrecognised key ',ord(k)
