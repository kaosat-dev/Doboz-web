import logging

from Core.connectors.event_sys import *
from ..hardware_node import HardwareNode

class WebcamNode(HardwareNode):
    """
    Dummy Node class, for testing purposes
    """
    def __init__(self):
        self.logger=logging.getLogger("Doboz.Core.WebcamNode")
        self.logger.setLevel(logging.ERROR)
        
        self.isRunning=False  
        self.connector=None 
        self.driver=None
        self.automation=None
        self.components=[]
        self.filePath=None
        self.logger.critical("Webcam Node Init Done")
        
    def set_connector(self,connector):
        """Sets what connector to use """
        self.connector=connector
        if hasattr(self.connector, 'events'):    
             #self.connector.events.OnDataRecieved+=self.data_recieved
             self.connector.events.disconnected+=self.on_connector_disconnected
             self.connector.events.reconnected+=self.on_connector_reconnected
        self.connector.start()   
    
    def start(self):
        self.connector.set_capture(self.filePath,2)
        
    def on_connector_disconnected(self,args,kargs):
        """
        Function that handles possible Webcam connector disconnection
        """
        self.logger.critical("Webcam connector disconnected !!!")
        self.isPaused=True
    
       
    def on_connector_reconnected(self,args,kargs):
        """
        Function that handles possible Webcam connectorreconnection
        """ 
        self.logger.critical("Webcam connectorreconnected !!!")