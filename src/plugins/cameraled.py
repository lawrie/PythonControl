from interfaces.led import LED

import RPi.GPIO as GPIO

class CameraLED(LED):
    """ Camera LED.
    """
    
    def __init__(self):
    	GPIO.setup(11,GPIO.OUT)
    	
    def turnOn(self):
        """ Turn on the LED.
        """
        GPIO.output(11,True)
        
    def turnOff(self):
        """ Turn off the LED.
        """
        GPIO.output(11,False)