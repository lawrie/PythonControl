from interfaces.arm import Arm

class MaplinArm(Arm):
    """ Maplin arm.
    """
    
    def __init__(self):	
		dev = usb.core.find(idVendor=0x1267, idProduct=0x0000)
		
		#exit if device not found
		if dev is None:
		  raise ValueError('Can\'t find robot arm!')
		
		#this arm should just have one configuration...
		dev.set_configuration()
    
    def shoulder(self, n):
        """ Move the shoulder.
        """
        movearm("SHOULDER",n)
        
    def elbow(self, n):
        """ Move the elbow.
        """
        movearm("ELBOW",n)
        
    def wrist(self, n):
        """ Move the wrist.
        """
        movearm("WRIST",n)
        
    def base(self, n):
        """ Move the base.
        """
        rotatebase(n)
        
   	def gripper(self, n):
        """ Move the gripper.
        """
        movearm("GRIP",n)
        
  	def movearm(joint,cval): 	
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
	    
	def rotatebase(cval):
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