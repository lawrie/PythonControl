import serial
import time

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
  
def set_position(rotation, stretch, height, wrist, catch):
  ser1.write(chr(0xFF) + chr(0xAA) + chr(rotation >> 8 & 0xff) + chr(rotation & 0xff) + chr(stretch >> 8 & 0xff) + chr(stretch & 0xff) + chr(height >> 8 & 0xff) + chr(height & 0xff) + chr(wrist >> 8 & 0xff) + chr(wrist & 0xff) + chr(catch))

#main
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
ser1 = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)
speed = 200

rotation = 0
stretch = 0
height = 0
wrist = 0
catch = 0

while 1:
  sensors = updatesensors()
  catch = 0
  k = getch()

  if k == "l": rotation -= 1
  elif k == "L": rotation -= 5
  elif k == "r": rotation += 1
  elif k == "R": rotation += 5
  elif k == "u": height += 1
  elif k == "U": height += 5
  elif k == "d": height -= 1
  elif k == "D": height -= 5
  elif k == "f": stretch += 1
  elif k == "F": stretch += 5
  elif k == "b": stretch -= 1
  elif k == "B": stretch -= 5
  elif k == "o": catch = 1
  elif k == "g": catch = 2
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
    
  set_position(rotation, stretch, height, wrist, catch)
