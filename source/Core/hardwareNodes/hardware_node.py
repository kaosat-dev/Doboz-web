import logging
import time
import datetime

class HardwareNode(object):
    """
    Base class for all hardware nodes: a hardware node is a software component handling a physical device such as a webcam, reprap , arduino etc
    """
    def __init__(self):
        self.logger=logging.getLogger("Doboz.Core.HardwareNode")
        self.logger.setLevel(logging.ERROR)
        self.isRunning=False  
        self.connector=None 
        self.automation=None
        self.components=[]
        
        """For Uptime calculation"""
        self.startTime=time.time()
        
    def set_driver(self,driver):
        """Sets what driver to use """
        self.driver=driver
        
    def connector_connected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  
    
    def connector_disconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"
      
    def connector_reconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  

       