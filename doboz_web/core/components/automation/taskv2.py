import logging
import time
import datetime
import sys
import os


from pollapli.core.tools.event_sys import *


class AutomationEvents(Events):
    __events__=("started","finished","actionDone")
    

class Task(object):
    """
    Base class for tasks (3dprinting , sensor data capture etc)
    """
    def __init__(self,type=None):
    
        self.connector=None
        self.type=type
            
        self.startTime=time.time()        
        self.totalTime=0
        
        self.progressFraction=0
        self.progress=0
        self.status="NP" #can be : NP: not started, paused , SP: started, paused, SR:started, running
        self.id=-1
        
        self.events=AutomationEvents()
        
        self.conditions=[]
    
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
        """
        When taks is started
        """
        self.events.started(self,"started")
        
    def exit(self):
        """
        When taks is finished
        """
        self.events.finished(self,"finished")
            
    def connect(self,connector):
        pass
    def disconnect(self):
        pass
    
    

    def _do_action_step(self):
        """
        do sub action in task
        """
        raise NotImplementedException("This needs to be implemented in a subclass")
    
    def check_task_conditions(self):
        """
        method in charge of verifying all of the tasks conditions
        for a task to start/continue running, all of its conditions must evaluate to True 
        """
        [condtion.check() for condition in self.conditions]
