from Core.connectors.event_sys import *

class HardwareConnectorEvents(Events):
    """
    Class defining events associated to HardwareConnector Class
    """
    __events__=('OnDataRecieved','OnConnected', 'OnDisconnected', 'OnReconnected')
    
class HardwareConnector(object):
    def __init__(self,driver=None):
        self.driver=driver
        
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