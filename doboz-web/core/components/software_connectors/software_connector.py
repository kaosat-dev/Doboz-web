from core.tools.event_sys import *

class HardwareConnectorEvents(Events):
    """
    Class defining events associated to HardwareConnector Class
    """
    __events__=('OnDataRecieved','connected', 'disconnected', 'reconnected')


  
class SoftwareConnector(object):
    """
    Base class for software connectors : to standardize the connection api to any (generally external) software : twitter, mail , etc
    """ 
    def __init__(self,driver=None):
        pass
        
        
    def connect(self,*args,**kwargs):
        """
        Establish connection to hardware
        """
        raise NotImplementedException()
    
    def fetch_data(self):
        """cheap hack for now"""
        pass
    
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