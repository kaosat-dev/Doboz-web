from doboz_web.core.tools.event_sys import *

class HardwareConnectorEvents(Events):
    """
    Class defining events associated to HardwareConnector Class
    """
    __events__=('OnDataRecieved','connected', 'disconnected', 'reconnected')


  
class HardwareConnector(object):
    def __init__(self,driver=None):
        self.isConnected=False
        self.currentErrors=0
        self.maxErrors=5
        self.driver=None
        self.events=HardwareConnectorEvents()
        
    def set_driver(self,driver):
        """Sets what driver to use : a driver formats the data sent to the connector !!"""
        self.driver=driver
        
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