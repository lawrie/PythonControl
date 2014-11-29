from interfaces.control import Control

class Robot(Control):
    """ Interface for mobile robots.
    """
    
    def travel(self, n):
        """ Travel in a line.
        """
        pass
        
    def rotate(self, n):
        """ Rotate on the spot.
        """
        pass