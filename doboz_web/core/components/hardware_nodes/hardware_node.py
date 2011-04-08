"""
.. py:module:: hardware_node
   :synopsis: hardware node for reprap handling.
"""

import logging
import time
import datetime
import uuid

class HardwareNode(object):
    """
    Base class for all hardware nodes: a hardware node is a software component handling a physical device such as a webcam, reprap , arduino etc
    """
    def __init__(self):
        self.logger=logging.getLogger("Doboz.doboz_web.core.HardwareNode")
        self.logger.setLevel(logging.ERROR)
        self.isRunning=False  
        self.connector=None 
        self.automation=None
        self.tasks=[]
        self.currentTask=None
        self.components=[]
        
        """For Uptime calculation"""
        self.startTime=time.time()
        
    def set_driver(self,driver):
        """Sets what driver to use : NOT IMPLEMENTED FOR NOW!!"""
        self.driver=driver
    
    def add_task(self,task):
        """
        Adds the task to the tasklist, and if there are not tasks running, starts it
        TODO add weakref to task
        """
        self.tasks.append(task)
        task.id=str(uuid.uuid4())
        task.events.OnExited+=self._on_task_exited
        self.logger.critical ("Task %s added , %d remaining tasks before starting",task.id,len(self.tasks)-1)
        
        if not self.currentTask:
            self._start_next_task()
            
    def remove_task(self,id):
        """Removes the task with id==id ,if and only if the task is not already running """
        if not self.currentTask:    
                [self.tasks.remove(task) for task in self.tasks if task.id==id]
                self.logger.critical ("Task %s Removed ",task.id)         
        else:
            if id!=self.currentTask.id :
                [self.tasks.remove(task) for task in self.tasks if task.id==id]
                self.logger.critical ("Task %s Removed ",task.id)  
                
    def clear_tasks(self,forceStop=False):
        """Clears the task list completely 
        Params: forceStop: if set to true, the current running task gets stopped and removed aswell
        """
        if forceStop:
            self.stop_task()
            
        [self.tasks.remove(task) for task in self.tasks]
        
                
    def _start_next_task(self):
        """Starts the next task in line"""
        if len(self.tasks)>0:
            try:
                self.logger.critical ("Starting next task ,%g remaining tasks",len(self.tasks)-1)
                self.currentTask=self.tasks[0]
                print("currenttask",self.currentTask)
                self.currentTask.connect(self.connector)
                self.currentTask.start()
            except Exception as inst:
                self.logger.critical ("Error while starting next task in queue %s",str(inst))
                
    def stop_task(self):
        """Stops the currenlty running task """
        if self.currentTask:
            self.currentTask.stop()
                
    def _on_task_exited(self,args,kargs):
        """Handles the event when the task exited (whether force stopped or because it was finished """
        self._task_shutdown()
        self.logger.critical ("Task Finished ,%g remaining tasks",len(self.tasks))
        self._start_next_task()
        
    def _task_shutdown(self):
        """helper function for cleaning up after a task ended """
        self.currentTask.disconnect()
        self.currentTask.events.OnExited-=self._on_task_exited
        self.currentTask=None 
        del self.tasks[0]          
                
        
    def _on_connector_connected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  
    
    def _on_connector_disconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"
      
    def _on_connector_reconnected(self,args,kargs):
        raise NotImplementedError, "This methods needs to be implemented in your node subclass"  

       