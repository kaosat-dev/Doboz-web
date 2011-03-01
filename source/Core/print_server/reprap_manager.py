import logging
import time
import datetime
import sys
import os

from pyparsing import *
from decimal import *  

from Core.Tools.Serial.EventSys import*
from Core.Tools.Serial.queuable_serial import serial
from point_cloud import PointCloudBuilder,Point


class ReprapManagerEvents(Events):
    __events__=('OnLineParsed','OnTotalLinesSet','OnTotalLayersSet','OnPathSet','OnPositionChanged','OnScanHeightRecieved' )
    
class GCodeParser(object):
    def convertIntegers(self,tokens):
        return int(tokens[0])
    def convertFloats(self,tokens):
        return Decimal(tokens[0])
    def parse(self,line):
        result=None
    
        caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        point = Literal('.')
        plusorminus = Literal('+') | Literal('-')
        number = Word(nums).setParseAction( self.convertIntegers )
        integer = Combine(Optional(plusorminus) + number).setParseAction( self.convertIntegers )
        floatnumber = Combine(integer + 
                           Optional(point + Optional(number)) + 
                           Optional(integer)
                         ).setParseAction( self.convertFloats )
    
        prefix=(Word(caps)("key")+number("value"))("prefix")
        subelement=Optional((Word(caps)("ty") +floatnumber("value")) , default="None")("element")
            
        xcmd=Optional((Literal('X')("key")+floatnumber("value")) , default=None)("xcmd")
        ycmd=Optional((Literal('Y')("key")+floatnumber("value")) , default=None)("ycmd")
        zcmd=Optional((Literal('Z')("key")+floatnumber("value")) , default=None)("zcmd")
        ecmd=Optional((Literal('E')("key")+floatnumber("value")) , default=None)("ecmd")        
        fcmd=Optional((Literal('F')("key")+floatnumber("value")) , default=None)("fcmd")   
        scmd=Optional((Literal('S')("key")+floatnumber("value")) , default=None)("scmd")     
    
        subcmd=prefix+(xcmd+ycmd+zcmd+ecmd+fcmd+scmd)("subs")
        commands=[]   
        val=0
        try:            
            content=subcmd.parseString(line)
            result=content
        except:
            pass
        return result
#            print("prefix",content.prefix.key,content.prefix.value)
#            print("subs",content.subs)
#            
#            try:
#                print("sub test",content.subs[0])
#                print("sub test2",content.xcmd)
#                print("sub test2",content.xcmd.key)
#                print("sub test2",content.xcmd.value)
#            except:
#                pass
#            return content
#        except:
#            pass
        

class ReprapManager(object):
    def __init__(self,serl=None):
         
        self.logger=logging.getLogger("Doboz.Core.ReprapManager")
        self.logger.setLevel(logging.ERROR)
        if not logging.getLogger("Doboz.Core").handlers:           
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.ERROR)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch) 
         
        if serl is None:
            self.serial=serial(seperator="\r\n",isBuffering=True,Speed=19200)
        else:
            self.serial=serl
         
        if hasattr(self.serial, 'events'):    
             self.serial.events.OnDataRecieved+=self.data_recieved
             self.serial.events.OnPortDisconnected+=self.on_serial_disconnect
             self.serial.events.OnPortReconnected+=self.on_serial_reconnect


        """ """
        self.rootPath=None
        """For all things related to the print positioning tracking """           
        self.gcodeParser=GCodeParser()
        self.position=[0,0,0]
        self.positionList=[]
        
        """For all things related to the scanning   """
        self.pointCloudBuilder=PointCloudBuilder(0.1,10,10)
        self.pointCloudSavePath=None
        """ """
        self.bedTemp=0
        self.headTemp=0
        
                 
        self.events=ReprapManagerEvents() 
        self.sourcePath=""
        self.source=None
        self.isStarted=False
        self.recoveryMode=False
        self.isPaused=True
        self.pauseRequested=False
        self.mode="Print" #can be scan or print
       
        self.gcodeSuffix="\n"
        self.totalLines=1
        self.lastLine=None
        self.currentLine=0#for post error recup
        self.reconnectionCommand=None
        
        self.currentLayer=0
        self.totalLayers=0
        self.lastLayer=0#for layer counting
        
        self.totalTime=0#for total print time count
        self.startTime=time.time()
 
        #in %
        self.progressFraction=0
        self.progress=0

       
        self.serial.start()    
        self.logger.critical("Init Done")
       
       
    """
    Configure paths
    """
    def set_paths(self,rootPath):
         self.rootPath=rootPath
         self.pointCloudSavePath=os.path.join(rootPath,"scanFiles")
    """
    Init
    """
    def init(self):
         #for post error restart
        self.logFile=open("log.txt","r")
        logContent=self.logFile.read()
        self.logFile.close()
        if  logContent.find("ok")==-1:
            #read line
            self.logger.critical("last instance of program failed, loading up file")
            self.set_sourcePath_fromLog()
               
            
    """
    Start the whole system
    """
    def start(self):
        try:
                self.source=open(self.sourcePath,"r")
                self.forward_toLine(self.currentLine)#go to requested start line
                self.isStarted=True
                self.isPaused=False
                self.position=[0,0,0]
                self.positionList=[]
                self.send_nextLine()      
                self.totalTime=0
                self.progress=0
                self.startTime=time.time()  
               
        except:
                self.logger.critical("invalid gcode file")
                
    """
    Switches between active and inactive mode.
    """
    def startPause(self):
        self.isPaused=not self.isPaused
        if self.isPaused:
            self.logger.critical("Pausing")   
            #update elapsed time
            self.totalTime+=time.time()-self.startTime
        else:
            self.logger.critical("Starting")
            if self.isStarted:#is the system already running?
                self.startTime=time.time() 
                if self.mode=="Print":
                    self.send_nextLine()
                else:
                    self.do_scan_step()
            else:#if the system has not yet been started
                self.start()
    
    
    """
    Stops the current gcode file reading and resets everything to defaults
    """
    def stop(self):
        self.logger.critical("Stopped")
        try:
            self.source.close()
        except:
            pass
        self.isPaused=True
        self.isStarted=False
        #self.totalTime+=time.time()-self.startTime
    """
    clean shutdown mode
    """
    def quit(self):
        self.serial.tearDown()
        self.logFile=open("log.txt","a")
        self.logFile.write(", shutdown=ok") 
        self.logger.critical("quitting")
        
    
    """Scan method """
    def scan(self,scanWidth,scanLength,resolution):
        self.isStarted=True
        self.pointCloudBuilder=PointCloudBuilder(resolution,scanWidth,scanLength)
        self.progress=0
        totalPoints=(int(scanWidth/resolution)+1)*(int(scanLength/resolution)+1)
        self.logger.info("Total scan points %d",totalPoints)
        self.progressFraction=float(100.00/float(totalPoints))
        self.logger.info("Progress Fraction set by scan to %s",str(self.progressFraction))


        #######################
        self.sendText("G21")
        self.sendText("G90")
        self.sendText("G92")
        self.mode="Scan"
        self.isPaused=False
        
        ptBld=self.pointCloudBuilder.currentPoint
        self.sendText("G1 X"+str(ptBld.x)+" Y"+str(ptBld.y))
        
        
  
    def do_scan_step(self):
        #move the printhead , ask for scan, wait for answer
        if not self.pointCloudBuilder.finished:
            self.progress+=self.progressFraction
            ptBld=self.pointCloudBuilder.currentPoint
            self.sendText("G1 X"+str(ptBld.x)+" Y"+str(ptBld.y))
            
            
        else:
            self.progress=100
            self.sendText("G1 X0 Y0")
            self.pointCloudBuilder.pointCloud.save(self.pointCloudSavePath)
            self.isStarted=False
            self.isPaused=True

    
            
    """
    Simple function to send text over serial
    """
    def sendText(self,text):
        self.serial.send_data(text+self.gcodeSuffix)   
              
    """
    gets the next line in the gCode file, sends it via serial, updates the logFile
    and then increments the currentLine counter
    """
    def send_nextLine(self):
        try:
            line = self.source.readline()
            self.line=line
        except :
            pass
        if line is not None:
            text_suffixed=line+self.gcodeSuffix
            self.serial.send_data(text_suffixed)   
            """
            Update the logfile with the current Line number
            """
            self.logFile=open("log.txt","w")
            self.logFile.write("path="+str(self.sourcePath)+",")  
            self.logFile.write(" ")
            self.logFile.write("line="+str(self.currentLine))
            self.logFile.close()
            
            self.logger.critical("Sent command "+ line)
            self.events.OnLineParsed(self,line)
            self.currentLine+=1
            self.lastLine=line
            
            if (self.currentLine+1)==self.totalLines:
                self.progress=100
                self.isStarted=False
            else:
                self.progress+=self.progressFraction
            
            pos=self.gcodeParser.parse(line)
            if pos:
                try:
                    #self.position=[pos.xcmd.value.to_eng_string(),pos.zcmd.value.to_eng_string(),pos.ycmd.value.to_eng_string()]
                    x=pos.xcmd.value/10
                    y=pos.ycmd.value/10
                    z=pos.zcmd.value/10
                    pt=Point(float(x.to_eng_string()),float(y.to_eng_string()),float(z.to_eng_string()))
                    self.positionList.append(pt)
                    #self.positionList.append(z.to_eng_string())
                    #self.positionList.append(y.to_eng_string())
                   
                except Exception as inst:
                    self.logger.critical("failed to add point to movement map %s",str(inst))
            
            
            self.totalTime+=time.time()-self.startTime
            self.startTime=time.time()
            
            
                                #add layer increase handling
#                    self.currentLayer
#                    if 
#                    self.events.On  
   
       
    """
    Function that gets called each time a new serial event is recieved.
    If the last command was confirmed, read next line frome gcode file, and 
    send it over serial.
    """
    def data_recieved(self,args,kargs):
        self.logger.info("event recieved from reprap %s",str(kargs))
        if self.mode=="Print":
            if self.reconnectionCommand and self.isStarted:
                if self.reconnectionCommand in kargs:
                    print ("reconnected command found")
                    self.reconnectionCommand=None
                    self.isPaused=False
            if not self.isPaused:
                if "ok" in kargs or "start" in kargs:
                    self.send_nextLine()    
        else:
            #in scan mode
            if "ok" in kargs:
                if "height" in kargs:  
                    height=float(kargs.split(' ')[2])
                    height=height/200
                    self.logger.info("Scan thing %s",str(height))
                    self.events.OnScanHeightRecieved(height)
                    self.pointCloudBuilder.add_point(height) 
                    if not self.isPaused:    
                        self.do_scan_step()

                else:
                    if not "G92" in kargs and not "G90" in kargs and not "G21" in kargs and "G1" in kargs and not self.isPaused:
                        self.sendText("M180")
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
            
    def get_status(self):
        pass
    """
    Function that handles possible serial port disconnection
    """
    def on_serial_disconnect(self,args,kargs):
        self.logger.critical("Serial port disconnected !!!")
        self.isPaused=True
    
    """
    Function that handles possible serial port reconnection
    """    
    def on_serial_reconnect(self,args,kargs):
        self.logger.critical("Serial port reconnected !!!")
        
        if self.lastLine and self.source and self.isStarted:
            time.sleep(5)
            self.sendText("G90")
            self.sendText("G92 "+self.lastLine[2:-1])
            self.reconnectionCommand="G1 "+self.lastLine[2:-1]
            print("RE INIT COMMAND",self.reconnectionCommand)     
            self.sendText(self.reconnectionCommand) 
           
            
           

    
    """
    Function to go to a specific line of the gcode file
    Params:
    lineNumber: the line we want to go to
    """
    def forward_toLine(self,lineNumber):
        line = self.source.readline()
        lineIndex=0
        
        while line:
            if lineIndex>=self.currentLine:
                self.currentLine=lineIndex
                print("going to line ",self.currentLine)
                break
            line = self.source.readline()
            lineIndex+=1
            
  
    
    """
    This function sets the current sourceFile, parses it for line numbers
    and layer count, sets everything up, and sends adapted events
    """    
    def set_sourcePath(self,sourcePath): 
        self.mode="Print"
        self.logger.critical("setting sourcePath: %s",sourcePath)
        self.sourcePath=sourcePath  
        self.stop()
        try:
            self.source=open(self.sourcePath,"r")
            if not self.recoveryMode:
                self.currentLine=0
                
            else:
                self.forward_toLine(self.currentLine)
            # define grammar
 
            point = Literal('.')
            plusorminus = Literal('+') | Literal('-')
            number = Word(nums)
            integer = Combine( Optional(plusorminus) + number )
            floatnumber = Combine( integer +
                       Optional( point + Optional(number) ) +
                       Optional( integer )
                     )
            
            xcmd=Dict(OneOrMore(Group('X'+floatnumber)))
            ycmd=Dict(OneOrMore(Group('Y'+floatnumber)))
            zcmd=Dict(OneOrMore(Group('Z'+floatnumber)))
            fcmd=Dict(OneOrMore(Group('Z'+floatnumber)))
            ecmd=Dict(OneOrMore(Group('E'+floatnumber)))
            
            
            subcmd = Literal('G1')+Optional(xcmd)+Optional(ycmd)+Optional(zcmd)+Optional(fcmd)+Optional(ecmd)
            
           
            self.totalLayers=0
            lastZ=0
            lineIndex=self.currentLine
            for line in self.source.readlines():          
               try:
                   content=subcmd.parseString(line).asDict()
                   if eval(content['Z'])!=lastZ:
                       self.totalLayers+=1
                   lastZ=eval(content['Z'])
               except:
                   pass
               lineIndex+=1   
            
            print(lineIndex)
            self.source.close()       
            self.totalLines=lineIndex - self.currentLine+1
            if self.totalLayers>2:
                self.totalLayers-=2

            self.events.OnTotalLinesSet(self,str(self.totalLines))
            self.events.OnTotalLayersSet(self,str(self.totalLayers))
            
            self.progressFraction=float(100/float(self.totalLines))
            self.logger.info("totalLines  %s",str(self.totalLines))
            self.logger.info("ProgressFraction set %s",str(self.progressFraction))
            self.progress=0
            
            self.logFile=open("log.txt",'w')
            self.logFile.write("path="+str(self.sourcePath))  
            self.logFile.close()
            
        except Exception  as inst:
            self.logger.critical("can't load file")
            print(inst.args)
            
    """
    This function is for recovery mode exclusively: it gets the params of the 
    last loaded gcode file and the last send gcode line from the log file
    """
    def set_sourcePath_fromLog(self):
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
        self.set_sourcePath(params["path="])
        
        self.events.OnPathSet(self,params["path="])
        
        self.recoveryMode=False

    
        
        
        
        

        
