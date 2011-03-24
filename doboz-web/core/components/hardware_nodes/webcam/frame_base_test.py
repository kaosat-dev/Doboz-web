import os
import sys
import time

import pygst
pygst.require("0.10")
import gst
import logging
from threading import Event, Thread
import gobject
gobject.threads_init()


class JustATest(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.logger=logging.getLogger("Doboz.core.GStreamerTest")
        self.logger.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.ERROR)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        self.player = gst.Pipeline("testpipeline")
        bus = self.player.get_bus()
        bus.set_sync_handler(self.on_message)
        
        self.finished=Event() 
        self.snapshotInterval=5
        self.filePath=None
        self.newRecording=False
     
    def on_message(self, bus, message):
        try:
            t = message.type
          
            if t == gst.MESSAGE_EOS:
                self.logger.info("Recieved eos message")
                #self.finished.set()
                self.newRecording=True
            elif t == gst.MESSAGE_ERROR:
                self.player.set_state(gst.STATE_NULL)
                
                err, debug = message.parse_error()
       
                self.logger.error("in GStreamer pipeline  %s: %s",err,debug)
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

        
    def init_capture(self):
        source=gst.element_factory_make("v4l2src","webcam_source")
        #source=gst.element_factory_make("ksvideosrc","webcam_source")
        #source.set_property("device-index", 0)
        ffmpegColorSpace=gst.element_factory_make("ffmpegcolorspace","ffMpeg1")
        ffmpegColorSpace2=gst.element_factory_make("ffmpegcolorspace","ffMpeg2")
        clockoverlay=gst.element_factory_make("clockoverlay","clock_overlay") 
        encoder=gst.element_factory_make("pngenc","png_encoder")
        fileSink= gst.element_factory_make("filesink", "file_destination")
        
        

        self.player.add(source,ffmpegColorSpace,clockoverlay,ffmpegColorSpace2, encoder, fileSink)
        gst.element_link_many(source,ffmpegColorSpace,clockoverlay,ffmpegColorSpace2, encoder, fileSink)
       
    
   
     
    def run(self):
        while not self.finished.isSet():
            if self.newRecording:
                self.player.set_state(gst.STATE_NULL)
                time.sleep(self.snapshotInterval)
                self.newRecording=False
                self.logger.info("Doing next snapshot")
                self.player.set_state(gst.STATE_PLAYING)
                
            else:
                time.sleep(0.1)
         

    def set_capture(self, filePath,interval):    
        self.filePath=filePath
        self.snapshotInterval=interval
        self.newRecording=True
        self.logger.critical("Starting capture to  %s",filePath)
        self.player.get_by_name("file_destination").set_property("location", filePath)
        self.player.get_by_name("clock_overlay").set_property("halign", "right")
        self.player.get_by_name("clock_overlay").set_property("valign", "bottom")


jst=JustATest()
#jst.init_FreqPlay()
#jst.freq()
jst.init_capture()
jst.set_capture(os.path.join(os.path.abspath("."),"test.png"),5)
#jst.set_capture(os.path.join("/home/ckaos/data/Projects/Doboz/source","core","print_server","files","static","img","test.png"),5)
jst.start()



