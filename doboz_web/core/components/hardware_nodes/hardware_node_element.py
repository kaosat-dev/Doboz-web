import logging


class HardwareNodeElement(object):
    def __init__(self,port=None,location=None,realName="n/a",name="DefaultName",description=""):
        self.logger=logging.getLogger("Hydroduino.Core.HardwareNodes.NodeElement")
        
        self.port=port
        self.location=location
        self.name=name
        self.realName=realName
        self.description=description
        self.connector=None
        self.automation=None
      
    def setup(self):
        """
        Configure Port
        """
        
    def activate(self):
        """
        Switch actor/sensor on:
        Params:
        """
        
    def deactivate(self):
        """
        Switch actor/sensor off:
        Params:
        """