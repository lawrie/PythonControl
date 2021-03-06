import serial
import time
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
speed = 200

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

while 1:
  sensors = updatesensors()
  k = getch()
  if k == 'f':
    forward()
  elif k == 'l':
    spinleft()
  elif k == 'b':
    backward()
  elif k == 'r':
    spinright()
  elif k == chr(3) or k == 'q':
    break
  elif k == 's':
    stop()
  elif k == 'm':
    motors()
  elif k == 'n':
    motors(0)
  elif k == 'p':
    spot()
  elif k == 'c':
    control()
  elif k == 'd':
    dock()
  elif ord(k) == 27:
    dummy = getch()
    k = getch()
    if ord(k) == 65:
      forward()
    elif ord(k) == 66:
      backward()
    elif ord(k) == 68:
      spinleft()
    elif ord(k) == 67:
      spinright()
    else:
      print 'Unrecognized special key ',ord(k)
  else:
    print 'Unrecognised key ',ord(k)

