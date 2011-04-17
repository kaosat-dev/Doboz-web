import logging
import time
import datetime
from threading import Thread,Event


from doboz_web.core.tools.event_sys import *
from doboz_web.core.components.automation.task import Task, AutomationEvents

class TimerTask(Task,Thread):
    def __init__(self,delay=0):
        Thread.__init__(self)
        Task.__init__(self,"Timer")
        self.logger=logging.getLogger("dobozweb.core.Automation.TimerTask")
        self.logger.setLevel(logging.ERROR)
        
        self.delay=delay
        self.finished=Event()
        
    def connect(self,connector):
        self.connector=connector
#        if hasattr(self.connector, 'events'):  
#            self.connector.events.OnDataRecieved+=self._data_recieved
#            self.connector.events.OnDisconnected+=self.on_connector_disconnect
#            self.connector.events.OnReconnected+=self.on_connector_reconnect 
        
    def disconnect(self):  
        """Dsiconnected the task from the connector: to remove event handling """ 
        #self.connector.events.OnDataRecieved-=self._data_recieved
        self.connector=None
        
    def start(self):
        self.status="SR"
        self.events.OnEntered(self,"Entered")
        Thread.start(self)
        
    def run(self):
        while not self.finished.isSet():
            self.connector.fetch_data()
            #self.events.ActionDone(self,"ActionDone")   
            time.sleep(self.delay)
            
    def stop(self):
        self.finished.set()
        self.status="NP"
        self.events.OnExited(self,"Exited")
        
        
        
   