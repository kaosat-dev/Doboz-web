from Core.Tools.event_sys import *

class HardwareConnectorEvents(Events):
    """
    Class defining events associated to HardwareConnector Class
    """
    __events__=('OnDataRecieved','connected', 'disconnected', 'reconnected')


  
class HardwareConnector(object):
    def __init__(self,driver=None):
        self.driver=driver
        self.isConnected=False
        self.currentErrors=0
        self.maxErrors=5
        self.events=HardwareConnectorEvents()
        
    def connect(self,*args,**kwargs):
        """
        Establish connection to hardware
        """
        raise NotImplementedException()
    
    def send_command(self,command):
        """
        Add a command to the hardware abstractions command queue
        """
        raise NotImplementedException()
        
    def add_command(self,command):
        """
        Add a command to the hardware abstractions command queue
        """
        raise NotImplementedException()
    
    def clear_commands(self):
        """
        Clear all the commands of the hardware abstraction's command queue
        """
        raise NotImplementedException()