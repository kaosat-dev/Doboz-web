import logging
import time
import datetime
import sys
import os
import uuid

from sys import getrefcount
#from Core.Tools.Serial.EventSys import*


from Core.connectors.event_sys import *
"""TODO: Make tasks in tasks be weak refs""" 
class ReprapManagerEvents(Events):
    __events__=('OnLineParsed','OnTotalLinesSet','OnTotalLayersSet','OnPathSet','OnPositionChanged')

class ReprapNode(object):
    """
    A reprap node : hardware node (ie "Arduino or similar with attached components such as sensors and actors: ie in the case of a reprap: endstops, temperature sensors, steppers, heaters")
    """
    def __init__(self):
        self.logger=logging.getLogger("Doboz.Core.ReprapNode")
        self.logger.setLevel(logging.ERROR)
    
        self.isRunning=False  
        self.connector=None 
        self.driver=None
        self.automation=None
        self.components=[]
        
        self.tasks=[]
        self.currentTask=None
        self.taskDelay=10;
        
        self.startTime=time.time()
        
      
        self.rootPath=None
        self.events=ReprapManagerEvents() 
        self.gcodeSuffix="\n"
        
        
        self.logger.critical("Reprap Node Init Done")
        
    def set_connector(self,connector):
        """Sets what connector to use """
        self.connector=connector
        if hasattr(self.connector, 'events'):    
             #self.connector.events.OnDataRecieved+=self.data_recieved
             self.connector.events.OnDisconnected+=self.on_connector_disconnect
             self.connector.events.OnReconnected+=self.on_connector_reconnect  
        self.connector.start()    
        
    def set_driver(self,driver):
        """Sets what driver to use """
        self.driver=driver
        
    def add_task(self,task):
        """
        TODO add weakref to task
        """
        self.tasks.append(task)
        task.id=str(uuid.uuid4())
        task.events.OnExited+=self.on_task_exited
        self.logger.critical ("Task %s added ",task.id)
        
        if not self.currentTask:
            self.start_next_task()
            
    def remove_task(self,id):
        if not self.currentTask:    
                [self.tasks.remove(task) for task in self.tasks if task.id==id]
                self.logger.critical ("Task %s Removed ",task.id)         
        else:
            if id!=self.currentTask.id :
                [self.tasks.remove(task) for task in self.tasks if task.id==id]
                self.logger.critical ("Task %s Removed ",task.id)  

    
    def start_next_task(self):
        if len(self.tasks)>0:
            try:
                self.logger.critical ("Starting next task ,%g remaining task",len(self.tasks))
                self.currentTask=self.tasks[0]
                print("currenttask",self.currentTask)
                self.currentTask.connect(self.connector)
                self.currentTask.start()
            except Exception as inst:
                self.logger.critical ("Error while starting next task in queue %s",str(inst))
            
    def on_task_exited(self,args,kargs):
        self.logger.critical ("Task Exited ")
        self.currentTask.disconnect()
        self.currentTask.events.OnExited-=self.on_task_exited
        #curId=self.currentTask.id
        self.currentTask=None 
        self.tasks.pop(0)
        #self.remove_task(curId)
        self.start_next_task()
           
        
    def stop_task(self):
        if self.currentTask:
            self.currentTask.stop()
            self.currentTask=None
            
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
        self.isStarted=True
        self.totalTime=0
        self.startTime=time.time()  
    
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
      
    def data_recieved(self,args,kargs):
        return
        self.logger.critical("event recieved from reprap %s",str(kargs))
        
    def on_connector_disconnect(self,args,kargs):
        """
        Function that handles possible serial port disconnection
        """
        self.logger.critical("Serial port disconnected !!!")
        self.isPaused=True
    
       
    def on_connector_reconnect(self,args,kargs):
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
