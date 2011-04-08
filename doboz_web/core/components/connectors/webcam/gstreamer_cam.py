import os
import sys
import time
import logging
from threading import Event, Thread
import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst
import shutil

from doboz_web.core.components.connectors.hardware_connector import HardwareConnector,HardwareConnectorEvents

class GStreamerCam(Thread,HardwareConnector):
    """
    Gstreamer based webcam connector
    """
    def __init__(self,driver=None):
        self.logger=logging.getLogger("Doboz.doboz_web.core.GStreamerTest")
        self.logger.setLevel(logging.CRITICAL)
        Thread.__init__(self)
        HardwareConnector.__init__(self)
       
        
        
        self.player = gst.Pipeline("testpipeline")
        bus = self.player.get_bus()
        bus.set_sync_handler(self.on_message)
        
        self.finished=Event() 
        self.filePath=None
        self.realPath=None

        self.recordingRequested=False
        self.recordingDone=True
        self.driver=driver#"v4l2src"
        
        self.setup()
      
     
    def on_message(self, bus, message):
        """
        Gstreamer message handling
        """
        try:
            t = message.type
          
            if t == gst.MESSAGE_EOS:
                self.logger.info("Recieved eos message")
                #self.finished.set()
                self.recordingDone=True
            elif t == gst.MESSAGE_ERROR:
                self.player.set_state(gst.STATE_NULL)
                err, debug = message.parse_error()
                self.logger.error("in GStreamer pipeline  %s: %s disconnected",err,debug)
                if self.isConnected:
                     self.events.disconnected(self,None)
                else:
                    self.isConnected=True
            elif t==gst.MESSAGE_SEGMENT_DONE:
                self.logger.info("Recieved segment done message")
            elif t== gst.MESSAGE_ELEMENT:
                self.logger.info("Recieved message element message")
            elif t== gst.MESSAGE_STATE_CHANGED:
                old, new, pending = message.parse_state_changed()
                self.logger.info("Recieved state changed message OLD: %s NEW %s",old,new)
            
            return gst.BUS_PASS
        except Exception as inst:
            self.logger.critical("Error in messaging: %s",str(inst))
        finally:
            return gst.BUS_PASS

        
    def setup(self):
        """
        Configure the gstreamer pipeline element  
        """
        source=gst.element_factory_make(self.driver,"webcam_source")  
            
        if self.driver=="ksvideosrc":  
            source.set_property("device-index", 0)
            
        ffmpegColorSpace=gst.element_factory_make("ffmpegcolorspace","ffMpeg1")
        ffmpegColorSpace2=gst.element_factory_make("ffmpegcolorspace","ffMpeg2")
        
        clockoverlay=gst.element_factory_make("clockoverlay","clock_overlay") 
        clockoverlay.set_property("halign", "right")
        clockoverlay.set_property("valign", "bottom")
        
        
        encoder=gst.element_factory_make("pngenc","png_encoder")
        fileSink= gst.element_factory_make("filesink", "file_destination")
        
        
        self.player.add(source,ffmpegColorSpace,clockoverlay,ffmpegColorSpace2, encoder, fileSink)
        gst.element_link_many(source,ffmpegColorSpace,clockoverlay,ffmpegColorSpace2, encoder, fileSink)
       
    
    def run(self):
        """Main loop"""
        while not self.finished.isSet():
            if self.recordingDone and self.recordingRequested:  
                self.logger.info("Doing next snapshot")
                #copy the temporary file to the final file name, to prevent display problems when the webserver tries to server a file currently beeing 
                #written by gstreamer 
                if os.path.exists(self.filePath+"tmp.png"):
                    shutil.copy2(self.filePath+"tmp.png", self.filePath+".png")
                self.player.set_state(gst.STATE_NULL)
                
                self.recordingRequested=False
                self.recordingDone=False
                self.player.set_state(gst.STATE_PLAYING)        
            else:
                time.sleep(0.1)
         
    def fetch_data(self): 
        self.recordingRequested=True

    def set_capture(self, filePath):    
        self.filePath=filePath
        self.newRecording=False
        self.logger.critical("Starting capture to  %s",filePath)
        self.player.get_by_name("file_destination").set_property("location", self.filePath+"tmp.png")




