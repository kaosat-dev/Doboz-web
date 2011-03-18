import os
import socket
import logging
import ConfigParser

from Core.connectors.serial.queuable_serial import * 
from Core.connectors.webcam.gstreamer_cam import * 
from Core.hardwareNodes.reprap.reprap_node import ReprapNode
from Core.hardwareNodes.webcam.webcam_node import WebcamNode
from Core.print_server.print_server import *



def configure_all():
    """
    Setup all pre required elements for reprap , webcam handling and webserver 
    """ 
    Config = ConfigParser.ConfigParser()
    rootPath=os.path.abspath(".")
    Config.read(os.path.join(rootPath,"config.cfg"))
    """"""""""""""""""""""""""""""""""""
    
    logger=logging.getLogger("Doboz.Core")
    logger.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.ERROR)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    """"""""""""""""""""""""""""""""""""
    """Reprap config elements"""
    reprapNode=ReprapNode()
    qs=QSerial(seperator="\r\n",isBuffering=True,Speed=19200)
    reprapNode.set_connector(qs)
    
    """"""""""""""""""""""""""""""""""""
    """WebCam config elements"""
    useWebcam=Config.getboolean("WebCam", "use")
    webcamDriver=Config.get("WebCam", "driver")
    if useWebcam:
         webcamNode=WebcamNode()
         webcamNode.filePath=os.path.join(rootPath,"Core","print_server","files","static","img","test")
         webcamConnector=GStreamerCam(driver=webcamDriver)
         webcamNode.set_connector(webcamConnector)
         webcamNode.start()
    
    """"""""""""""""""""""""""""""""""""
    """Web Server config elements"""
    server=server=Config.get("WebServer", "server")
    port=Config.getint("WebServer", "port")
    testBottle.chosenServer=server
    testBottle.chosenPort=port
    testBottle.reprapManager=reprapNode
    


configure_all()
start_webServer()


