
"""
.. py:module:: webcam_node
   :synopsis: hardware node for webcam handling. 
"""

import logging

from doboz_web.core.tools.event_sys import *
from ..hardware_node import HardwareNode

class WebcamNode(HardwareNode):
    """
    webcam Node class
    """
    def __init__(self):
        self.logger=logging.getLogger("Doboz.doboz_web.core.WebcamNode")
        self.logger.setLevel(logging.ERROR)
        HardwareNode.__init__(self)
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
             self.connector.events.disconnected+=self._on_connector_disconnected
             self.connector.events.reconnected+=self._on_connector_reconnected
        self.connector.start()   
    
    def start(self):
        """
        Sets up the capture process
        """
        self.connector.set_capture(self.filePath)
        self.logger.critical("Starting Webcam Node")
        
    def _on_connector_disconnected(self,args,kargs):
        """
        Function that handles possible Webcam connector disconnection 
        """
        self.logger.critical("Webcam connector disconnected !!!")
        self.isPaused=True
    
       
    def _on_connector_reconnected(self,args,kargs):
        """
        Function that handles possible Webcam connectorreconnection
        """ 
        self.logger.critical("Webcam connectorreconnected !!!")