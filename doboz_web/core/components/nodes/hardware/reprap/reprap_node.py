
"""
.. py:module:: reprap_node
   :synopsis: hardware node for reprap handling.
"""

import logging
import time
import datetime
import sys
import os




from doboz_web.core.tools.event_sys import *
from ..hardware_node import HardwareNode

"""TODO: Make tasks in tasks be weak refs""" 
class ReprapManagerEvents(Events):
    __events__=('OnLineParsed','OnTotalLinesSet','OnTotalLayersSet','OnPathSet','OnPositionChanged')

class ReprapNode(HardwareNode):
    """
    A reprap node : hardware node (ie "Arduino or similar with attached components such as sensors and actors: ie in the case of a reprap: endstops, temperature sensors, steppers, heaters")
    """
    def __init__(self):
        self.logger=logging.getLogger("dobozweb.core.ReprapNode")
        self.logger.setLevel(logging.ERROR)
        HardwareNode.__init__(self)
 
        
        self.startTime=time.time()

        self.rootPath=None
        self.events=ReprapManagerEvents() 
        self.gcodeSuffix="\n"
        
            
        self.logger.critical("Reprap Node Init Done")
        
    def set_connector(self,connector):
        """
        Sets what connector to use
         
        """
        self.connector=connector
        if hasattr(self.connector, 'events'):    
             self.connector.events.disconnected+=self._on_connector_disconnected
             self.connector.events.reconnected+=self._on_connector_reconnected  
             self.connector.events.OnDataRecieved+=self._on_data_recieved
        self.connector.start()    
         
    def set_paths(self,rootPath):
        """
        Configure paths
        """
        self.rootPath=rootPath

    def startPause(self):
        """
        Switches between active and inactive mode.
        """
        if self.currentTask:
            self.currentTask.startPause()
           
    
    def start(self):
        """
        Start the whole system
        """          
        self.isRunning=True
        self.isStarted=True
        self.totalTime=0
        self.startTime=time.time()  
        self.logger.critical("Starting Reprap Node")
    
    def stop(self):
        """
        Stops the current task and shuts down
        """
        self.logger.critical("Stopped")
        self.isPaused=True
        self.serial.tearDown()
        #self.totalTime+=time.time()-self.startTime
    
    def sendText(self,text):
        """
        Simple function to send text over serial
        """
       
        self.serial.send_data(text+self.gcodeSuffix)   
      
    def _on_data_recieved(self,args,kargs):
        self.logger.debug("event recieved from reprap %s",str(kargs))
        try:
            answer=kargs.answer
            if  "T:" in answer:
                try:
                    raw=answer.split(' ')
                    self.headTemp=float(raw[0].split(':')[1])
                    self.bedTemp=float(raw[1].split(':')[1])
                except Exception as inst:
                    self.logger.critical("Error in temperature readout %s"%str(inst))
        except:
            pass
       
        
         #   self.logger.critical("Bed Temperature: %d Extruder Temperature %d",self.bedTemp,self.headTemp)

        
    def _on_connector_disconnected(self,args,kargs):
        """
        Function that handles possible serial port disconnection
        """
        self.logger.critical("Serial port disconnected !!!")
        self.isPaused=True
    
       
    def _on_connector_reconnected(self,args,kargs):
        """
        Function that handles possible serial port reconnection
        """ 
        self.logger.critical("Serial port reconnected !!!")
        
#        if self.lastLine and self.source and self.isStarted:
#            time.sleep(5)
#            self.connector.send_command("G90")
#            self.connector.send_command("G92 "+self.lastLine[2:-1])
#            self.reconnectionCommand="G1 "+self.lastLine[2:-1]
#            print("RE INIT COMMAND",self.reconnectionCommand)     
#            self.connector.send_command(self.reconnectionCommand) 
