import serial

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)

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

def set_position(rotation, stretch, height, wrist, catch):
  ser.write(chr(0xFF) + chr(0xAA) + chr(rotation >> 8 & 0xff) + chr(rotation & 0xff) + chr(stretch >> 8 & 0xff) + chr(stretch & 0xff) + chr(height >> 8 & 0xff) + chr(height & 0xff) + chr(wrist >> 8 & 0xff) + chr(wrist & 0xff) + chr(catch))

rotation = 0
stretch = 0
height = 0
wrist = 0
catch = 0
   
while 1:
  set_position(rotation, stretch, height, wrist, catch)
  catch = 0
  k=getch() 
  if k == 'l':
    rotation -= 1
  elif k == 'r':
    rotation += 1
  elif k == 'u':  
    height += 1
  elif k == 'd':
    height -= 1
  elif k == 'f':
    stretch += 1
  elif k == 'b':
    stretch -= 1
  elif k == 'c':
    catch = 1
  elif k == 'x':
    catch = 2
  elif k == chr(3) or k == 'q':
    break
    
ser.close()
     