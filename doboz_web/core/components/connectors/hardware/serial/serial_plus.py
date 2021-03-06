from __future__ import absolute_import
from collections import deque
from threading import Thread
from serial import Serial, SerialException
from threading import *
from random import *
import  time
import datetime
import logging
import os
import glob
import re
import sys
import itertools


from doboz_web.core.components.connectors.hardware.hardware_connector import HardwareConnector,HardwareConnectorEvents


class SerialPlus(Thread,HardwareConnector):
    """
    Class for sending out events each time data is sent through the observed serial port
    """
    blockedPorts=[]
    """A class level list of all , already in use serial ports: neeeded for multiplatform correct behaviour of serial ports """
    
    def __init__(self,pseudoName="serial",port=None,isBuffering=True,seperator='\r\n',Speed=115200,bannedPorts=None,maxErrors=5,waitForAnswer=False,protocol=None):
        """ Inits the thread
        Arguments:
            port -- serial port to be used, if none, will scan for available ports and 
            select the first one.
            isBuffering -- should it buffer up recieved serial data.
            seperator --only used with isBuffering: if specified, buffered data
            will be split by this seperator : each time a seperator is found, all data
            up until it is dispatched via an event
            speed -- serial port speed
        """
        self.logger = logging.getLogger("dobozweb.core.connectors.Serial")
        self.logger.setLevel(logging.INFO)
        
        Thread.__init__(self)
        HardwareConnector.__init__(self)
        

        self.waitForAnswer=waitForAnswer
        self.pseudoName=pseudoName
        self.port=port
        self.speed=Speed
        
        self.seperator=seperator
        self.isBuffering=isBuffering
        self.buffer=""
        
        self.finished=Event()
        
        if bannedPorts:
            for bPort in bannedPorts:
                if not bPort in serial.blockedPorts:
                    serial.blockedPorts.append(bPort)

        self.serial=None
        

        
        self.lastCommand=""
        
    def reset_seperator(self):
        self.regex = re.compile(self.seperator)
    
    def upload(self):
        avrpath="/home/ckaos/data/Projects/Doboz/doboz_web/core/tools/avr"
        cmd=os.path.join(avrpath,"avrdude")
        conf=os.path.join(avrpath,"avrdude.conf")
    
    def connect(self):
        """Port connection/reconnection procedure"""    
        try:
            serial.blockedPorts.remove(self.port)
        except:
            pass
        try:
            self.finished.clear()
        except:
            pass
        self.currentErrors=0
        self.port=None
        while self.port is None and self.currentErrors<5:
            try:      
                self.port=str(self.scan()[0])
                #TODO: weird: port init fails if following line is removed
                #print("Ports:",self.scan())
                SerialPlus.blockedPorts.append(self.port)        
                self.logger.critical("selecting port %s",str(self.port))
                self.serial=Serial(self.port,self.speed)
                
            except Exception as inst:
                self.logger.critical("cricital error while (re-)starting serial connection : please check your driver speed,  cables,  and make sure no other process is using the port ")
                self.currentErrors+=1
                time.sleep(self.currentErrors*5)
        if not self.port :
            self.tearDown()
        else:
            self.logger.info("(re)starting serial listener")
            if self.isConnected:
                self.events.reconnected(self,None)
            else:
                self.isConnected=True
                #self.start()
                
    def list_ports(self):
        """
        Return a list of ports
        """
        foundPorts=[]
        if sys.platform == "win32":
            import _winreg as winreg
            path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            except WindowsError:
                raise EnvironmentError
            for i in itertools.count():
                try:
                    val = winreg.EnumValue(key, i)
                    #foundPorts.append((str(val[1])), str(val[0]))#returns tuple: simpleName, fullName
                    foundPorts.append(str(val[1]))
                except EnvironmentError:
                    break
        else:
            foundPorts= glob.glob('/dev/ttyUSB*')+ glob.glob('/dev/cu*')
        #self.logger.info("Serial Ports on  system:",+str(foundPorts))
        return foundPorts
    
    def scan(self):
        """scan for available ports.
        Returns a list of actual available ports"""
        available = []
        
        for port in self.list_ports():  
            if port not in SerialPlus.blockedPorts: 
                try:
                    s = Serial(port) 
                    available.append(s.portstr)
                    s.close()   
                except SerialException:
                    pass
        if s is None:
            self.logger.info("failed to get port")
     
        #for n in available:
        #    print " %s" % (n)
        return available
        
    def run(self):
        """
        Main loop in thread, checks for new recieved data on the serial port at a regular interval
        If buffered mode is active and a seperator set, all data is added to the current data
        buffer until a seperator is found, and then an event containing the datablock (up until the 
        seperator) is dispatched
        """
        while not self.finished.isSet():
            if not self.isConnected:
                self.connect()
            else:   
                nextCommand=self.driver.get_next_command()
                if nextCommand:
                    self.send_command(nextCommand)
                try:
                    data=None
                    data=self.get_data()
                    if data:
                        self.logger.debug("SERIAL GOT DATA %s", str(data))
                    
                    newDataTreated=True
                    
                    if data is not None:
                        newDataTreated=False
                        #in the case of buffering we fill the data buffer with all recieved data
                        #and as soon as we find a complete seperator, we split the substring ending with the seperator
                        #from the rest of the string and raise an event, sending the substring as message
                        if self.isBuffering:
                            self.logger.debug("serial buffering")
                            self.buffer+=str(data)
                        else:
                            self.logger.debug("standard serial")
                            self.events.OnDataRecieved(self,data)
                            
                    if self.isBuffering:
                        #if we have NOT already checked the last state of the data block
                        #then check it
                        if newDataTreated is False:
                            results=None
                            try:
                                results=self.regex.search(self.buffer)
                            except Exception as inst:
                                self.logger.critical("Error while parsing serial data :%s",str(inst))
                        
                            while results is not None:
                                    nDataBlock= self.buffer[:results.start()]
                                    self.lastCommand=nDataBlock
                                   
                                    if self.driver:
                                        nDataBlock=self.driver.handle_answer(nDataBlock)
                                        if nDataBlock:
                                            if nDataBlock.answerComplete:
                                                self.events.OnDataRecieved(self,nDataBlock)
                                                self.logger.critical("serial data block <<:  %s",(str(nDataBlock)))
                                    else:
                                        self.events.OnDataRecieved(self,nDataBlock)
                                        self.logger.critical("serial data block <<:  %s",(str(nDataBlock)))
                                   
                               
                                    
                                    self.buffer=self.buffer[results.end():]
                                    results=None
                                    try:
                                        results =self.regex.search(self.buffer)
                                    except:
                                        pass      
                            newDataTreated=True
    
                except SerialException:
                    self.logger.critical("serial Error")
            time.sleep(0.01)
        Thread.__init__(self)
                  
    def get_data(self):
        """
        Main funtion for getting the data recievd on the serial port
        If attemps to get the serial data fail,shutdown
        """
        data=None
        if self.isConnected :
            try:
                waiting=self.serial.inWaiting()
                if waiting>0:
                    self.logger.debug("waiting for data")
                    data=self.serial.read(waiting)
            except Exception,e:
                self.logger.critical("critical failure while getting serial data %s",str(e))
                self.currentErrors+=1
                #after ten failed attempts , shutdown
                if self.currentErrors>self.maxErrors:
                    self.events.disconnected(self,None)
                    self.connect()
                    
        return data

    def add_command(self,command,*args,**kwargs):
        """
        Ennqueue/add a command , via the driver:
        """
       
        if self.driver:
            self.driver.handle_request(command,*args,**kwargs)
        else:# without driver, no buffer , so just send the command
            self.send_command(command)
        self.logger.debug("new command appended: '%s'",str(command))
        
    def send_command(self,command,*args,**kwargs):  
        """
        Simple wrapper to send data over serial
        """    
        if self.isConnected: 
            try:
                self.logger.critical("serial data block >>: %s ",str(command))
                self.serial.write(command)
            except OSError:
                self.logger.critical("serial device not connected or not found on specified port")

    def disconnect(self):
        pass
    
    def tearDown(self):
        """
        Clean shutdown function
        """
        try:
            QSerial.blockedPorts.remove(self.port)
        except:
            pass
        self.isConnected=False
        while not self.finished.isSet():
            self.finished.set()
        self.logger.critical("Serial shutting down")
        if self.serial:
            self.serial.close()
        self.logger.info("Serial shut down")