import logging
import time
import datetime
import sys
import os


from Core.connectors.event_sys import *


class AutomationEvents(Events):
    __events__=("OnEntered","OnExited","ActionDone")
    

class Task(object):
    """
    Base class for tasks (printing , scanning etc
    """
    def __init__(self,type=None):
    
        self.connector=None
        self.type=type
            
        self.startTime=time.time()        
        self.totalTime=0#for total print/scan time count
        
        self.progressFraction=0
        self.progress=0
        self.status="NP" #can be : NP: not started, paused , SP: started, paused, SR:started, running
        self.id=-1
        
        self.events=AutomationEvents()
    
    def startPause(self):
        """
        Switches between active and inactive mode, or starts the task if not already done so
        """
        if self.status=="SR":
            self.status="SP"
            self.logger.critical("Pausing")   
            #update elapsed time
            self.totalTime+=time.time()-self.startTime
        elif self.status=="SP":
            self.status="SR"
            self.logger.critical("Un Pausing")
            self.startTime=time.time()   
            self._do_action_step()
            
    def enter(self):
        """"""
        self.events.OnEntered(self,"Entered")
        
    def exit(self):
        """"""
        self.events.OnExited(self,"Exited")

    def _do_action_step(self):
        raise NotImplementedException("This needs to be implemented in a subclass")
