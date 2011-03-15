import logging
import time
import datetime
import sys
import os

from Core.Tools.point_cloud2 import Point,PointCloud
from Core.Tools.point_cloud_builder import PointCloudBuilder
from Core.connectors.event_sys import *
from Core.automation.task import Task, AutomationEvents
from Core.automation.gcode_parser import GCodeParser

class PrintTask(Task):
    """ A task for printing gcode files"""
    def __init__(self,connector=None,filePath=None):
        Task.__init__(self,connector,"print")
        self.logger=logging.getLogger("Doboz.Core.Automation.PrintTask")
        self.logger.setLevel(logging.ERROR)
        
        
        self.filePath=filePath
        
        self.totalLines=1
        self.lastLine=None
        self.currentLine=0#for post error recup
        self.reconnectionCommand=None
        
        self.currentLayer=0
        self.totalLayers=0
        self.lastLayer=0#for layer counting
        

        self.source=None
        
        self.recoveryMode=False
        self.doLayerAnalysis=False
        self.gcodeSuffix="\n"
        
        """For all things related to the print positioning tracking """           
        self.gcodeParser=GCodeParser()
        
       
#        self.logFile=open("log.txt","r")
#        logContent=self.logFile.read()
#        self.logFile.close()
#        if  logContent.find("ok")==-1:
#            #read line
#            self.logger.critical("last instance of program failed, loading up file")
#            self.set_filePath_fromLog()
   
   
    def __str__(self):
        string='{"id": "%s", "type": "%s", "file": "%s"}' %(str(self.id), self.type, os.path.basename(self.filePath))
        return string   
    
    def connect(self,connector):
        self.connector=connector
        print(self.connector)
        if hasattr(self.connector, 'events'):  
            self.connector.events.OnDataRecieved+=self._data_recieved
#            self.connector.events.OnDisconnected+=self.on_connector_disconnect
#            self.connector.events.OnReconnected+=self.on_connector_reconnect 
    
    def disconnect(self):   
        self.connector.events.OnDataRecieved-=self._data_recieved
        self.connector=None
       # self.stop()
        
    def start(self):
        """ Starts the current print task"""
        self._set_filePath()
        try:
            self.source=open(self.filePath,"r")
            self._forward_toLine(self.currentLine)#go to requested start line
            self.status="SR"#actual first start
            self.events.OnEntered(self,"Entered")
            self._do_action_step()
            
        except Exception as inst:
            self.logger.critical("invalid gcode file %s",str(inst))
        
        
   
    def _forward_toLine(self,lineNumber):
        """
        Function to go to a specific line of the gcode file
        Params:
        lineNumber: the line we want to go to
        """
        line = self.source.readline()
        lineIndex=0
        
        while line:
            if lineIndex>=self.currentLine:
                self.currentLine=lineIndex
                print("going to line ",self.currentLine)
                break
            line = self.source.readline()
            lineIndex+=1
      
    def _set_filePath(self): 
        """
        This function sets the current sourceFile, parses it for line numbers
        and layer count, sets everything up, and sends adapted events
        """ 
        self.logger.critical("setting filePath: %s",self.filePath)

        try:
            self.source=open(self.filePath,"r")
            if not self.recoveryMode:
                self.currentLine=0
            else:
                self.forward_toLine(self.currentLine)

            self.totalLayers=0
            lastZ=0
            lineIndex=self.currentLine
            for line in self.source.readlines(): 
                #TODO: some more inteligent "guestimate" of layers : read from the start, get two diferent z components, read from the end, get last Z component  
#                layerInfo=self.gcodeParser.parse(line)   
#                try: 
#                    zInfo=float(layerInfo.zcmd.value.to_eng_string())
#                    if zInfo!=lastZ:
#                        self.totalLayers+=1
#                        lastZ=zInfo
#                except:
#                    pass
                lineIndex+=1   
            
            self.source.close()       
            self.totalLines=lineIndex - self.currentLine+1
            if self.totalLayers>2:
                self.totalLayers-=2
            #self.logger.critical("Total layers %g",self.totalLayers)
            #self.events.OnTotalLinesSet(self,str(self.totalLines))
            #self.events.OnTotalLayersSet(self,str(self.totalLayers))
            
            self.progressFraction=float(100/float(self.totalLines))
            self.logger.info("totalLines  %s",str(self.totalLines))
            self.logger.info("ProgressFraction set %s",str(self.progressFraction))
            self.progress=0
            
            self.logFile=open("log.txt",'w')
            self.logFile.write("path="+str(self.filePath))  
            self.logFile.close()
            
        except Exception  as inst:
            self.logger.critical("can't load file %s",str(inst))

     
    def _set_filePath_fromLog(self):
        """
        This function is for recovery mode exclusively: it gets the params of the 
        last loaded gcode file and the last send gcode line from the log file
        """
        try:
            self.logFile=open("log.txt",'r')
            number = Word(nums)
            #parse last filePath and lineNumber
            path=Dict(OneOrMore(Group("path"+"="+SkipTo( "," | stringEnd ))))
            lastline=Dict(OneOrMore(Group("line"+'='+ number)))
           
            tmp=path+Optional(",")+Optional(lastline)
            ln=self.logFile.readline()
            params=tmp.parseString(ln).asDict()
            
            self.logFile.close()    
            self.recoveryMode=True
            try:
                self.currentLine=eval(params["line="]) 
                #skip one line : it is better to lose one command than loose the print
                self.currentLine+=1
            except:
                self.currentLine=0
            self.set_filePath(params["path="])
            
            self.events.OnPathSet(self,params["path="])
            
            self.recoveryMode=False
        except:
            pass 
              
    def _do_action_step(self):
        """
        gets the next line in the gCode file, sends it via serial, updates the logFile
        and then increments the currentLine counter
        """
        try:
            line = self.source.readline()
            self.line=line
        except :
            pass
        if line is not None:
            text_suffixed=line+self.gcodeSuffix
            self.connector.send_command(text_suffixed)   
            """
            Update the logfile with the current Line number
            """
#            self.logFile=open("log.txt","w")
#            self.logFile.write("path="+str(self.filePath)+",")  
#            self.logFile.write(" ")
#            self.logFile.write("line="+str(self.currentLine))
#            self.logFile.close()
            
            self.logger.critical("Sent command "+ line)
#            self.events.OnLineParsed(self,line)
            self.currentLine+=1
            self.lastLine=line
            if (self.currentLine+1)==self.totalLines:
                self.progress=100
                self.status="F"
            else:
                self.progress+=self.progressFraction

            
            pos=self.gcodeParser.parse(line)

            if pos:
                try:
                    #self.position=[pos.xcmd.value.to_eng_string(),pos.zcmd.value.to_eng_string(),pos.ycmd.value.to_eng_string()]
                    x=float(pos.xcmd.value.to_eng_string())/20
                    y=float(pos.ycmd.value.to_eng_string())/20
                    z=float(pos.zcmd.value.to_eng_string())/20
                    self.pointCloud.add_point(Point(x,y,z))             
                except Exception as inst:
                    self.logger.critical("failed to add point to movement map %s",str(inst))
            
            self.totalTime+=time.time()-self.startTime
            self.startTime=time.time()
            
    def _data_recieved(self,args,kargs):
        """
        Function that gets called each time a new serial event is recieved.
        If the last command was confirmed, read next line frome gcode file, and 
        send it over serial.
        """
        self.logger.info("event recieved from reprap %s",str(kargs))
       
        if self.reconnectionCommand and self.status=="SP":
            if self.reconnectionCommand in kargs:
                print ("reconnected command found")
                self.reconnectionCommand=None
 
        if self.status!="NP" and self.status!="SP":#not paused
            if "ok" in kargs or "start" in kargs:
                self._do_action_step()    
       
        if "ok" in kargs  and "M105" in kargs:
            try:
                self.headTemp=int(kargs.split(' ')[1])
            except:
                pass
        if "ok" in kargs  and "M143" in kargs:
            try:
                self.bedTemp=int(kargs.split(' ')[1])
            except:
                pass
            

    def stop(self):
        """
        clean shutdown mode
        """
        self.status="NP"
        try:
            self.source.close()
        except:
            pass
        self.logFile=open("log.txt","a")
        self.logFile.write(", shutdown=ok") 
        self.events.OnExited(self,"OnExited")