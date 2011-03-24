import logging
import time
import datetime
import sys
import os

#from core.hardware_nodes.point_cloud import PointCloudBuilder,Point,PointCloud
from core.tools.point_cloud import Point,PointCloud
from core.tools.point_cloud_builder import PointCloudBuilder

from core.tools.event_sys import *
from core.components.automation.task import Task, AutomationEvents

#class ScanTaskEvents(Events):
#    __events__=('OnScanHeightRecieved' )  

class ScanTask(Task):
    """For all things related to the scanning   """    
    def __init__(self,scanWidth=1,scanLength=1,resolution=1,passes=1,filePath=None,saveScan=False):
        Task.__init__(self,"scan")
        self.logger=logging.getLogger("Doboz.core.Automation.ScanTask")
        self.logger.setLevel(logging.ERROR)
       
        self.width=scanWidth
        self.length=scanLength
        self.resolution=resolution
        self.filePath=filePath
        self.saveScan=saveScan
        
        self.pointCloud=PointCloud()        
        self.pointCloudBuilder=PointCloudBuilder(resolution=resolution,width=scanWidth,length=scanLength,passes=passes)
        totalPoints=(int(scanWidth/resolution)+1)*(int(scanLength/resolution)+1)*passes
        self.logger.info("Total scan points %d",totalPoints)
        self.progressFraction=float(100.00/float(totalPoints))
        self.logger.info("Progress Fraction set by scan to %s",str(self.progressFraction))
        
        self.logger.critical("Task Init Done")    
       
    def __str__(self):
        string='{"id": "%s", "type": "%s", "width": %s, "height":%f, "resolution": %s}' %(str(self.id), self.type,self.width,self.length,self.resolution)
        return string   
    
    def connect(self,connector):
        self.connector=connector
        if hasattr(self.connector, 'events'):  
            self.connector.events.OnDataRecieved+=self._data_recieved
#            self.connector.events.OnDisconnected+=self.on_connector_disconnect
#            self.connector.events.OnReconnected+=self.on_connector_reconnect 
             
    def disconnect(self):  
        """Dsiconnected the task from the connector: to remove event handling """ 
        self.connector.events.OnDataRecieved-=self._data_recieved
        self.connector=None
        
    def start(self):
        self.status="SR"#actual first start
        self.events.OnEntered(self,"Entered")
       #######################
        #Initialize base position
        self.connector.send_command("G21")
        self.connector.send_command("G90")
        self.connector.send_command("G92")

        ptBld=self.pointCloudBuilder.currentPoint
       
        self.connector.send_command("G1 X"+str(ptBld.x)+" Y"+str(ptBld.y))  

    def stop(self):
        self.status="NP"
        self.events.OnExited(self,"OnExited")
        
    def _do_action_step(self):
        #move the printhead , ask for scan, wait for answer
        if not self.pointCloudBuilder.finished:
            self.progress+=self.progressFraction
            ptBld=self.pointCloudBuilder.currentPoint
           
            self.connector.send_command("G1 X"+str(ptBld.x)+" Y"+str(ptBld.y))     
        else:
            self.progress=100
            self.pointCloud=self.pointCloudBuilder.pointCloud 
            self.status="F"#finished
            if self.saveScan:
                if self.filePath:
                    self.pointCloud.save(self.filePath)
                else:
                    pass
            self.connector.send_command("G1 X0 Y0")
            

    def _data_recieved(self,args,kargs):
        """
        Function that gets called each time a new serial event is recieved.
        If the last command was confirmed, move to next position and get height info
        """
        self.logger.info("event recieved from reprap %s",str(kargs))
        if self.status!="F":  
            if "ok" in kargs:
                if "height" in kargs:  
                    try:
                        height=float(kargs.split(' ')[2])
                        height=height/50
                        self.logger.info("Scan thing %s",str(height))
                        #self.events.OnScanHeightRecieved(height)
                        self.pointCloudBuilder.add_point(height) 
                        self.logger.critical("current point %s",str(self.pointCloudBuilder.currentPoint))
                        self.pointCloudBuilder.next_point_continuous()
                        self.pointCloud=self.pointCloudBuilder.pointCloud
                    except:
                        pass
                    if self.status!="NP" and self.status!="SP":   
                        self._do_action_step()
                else:
                    if not "G92" in kargs and not "G90" in kargs and not "G21" in kargs  and "G1" in kargs and self.status!="NP" and self.status!="SP" :
                        self.connector.send_command("M180")
                        
        else:
            if "ok" in kargs and "G1" in kargs:
                self.events.OnExited(self,"OnExited")
                    