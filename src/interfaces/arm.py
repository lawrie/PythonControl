from control import Control

class Arm(Control):
    """ Interface for robot arms.
    """
    
    def shoulder(self, n):
        """ Move the shoulder.
        """
        pass
        
    def elbow(self, n):
        """ Move the elbow.
        """
        pass
        
    def wrist(self, n):
        """ Move the wrist.
        """
        pass
        
    def base(self, n):
        """ Move the base.
        """
        pass
        
   def gripper(self, n):
        """ Move the gripper.
        """
        pass