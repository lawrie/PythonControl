from interfaces.robot import Robot

class Roomba(Robot):
    """ Roomba robot.
    """
    
    def __init__(self):
    	ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
		speed = 200
    
    def travel(self, n):
        """ Travel in a line.
        """
        pass
        
    def rotate(self, n):
        """ Rotate on the spot.
        """
        pass
   
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