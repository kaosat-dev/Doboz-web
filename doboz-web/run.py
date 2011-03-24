#!python
"""
.. py:module:: run
   :platform: Unix, Windows, Mac
   :synopsis: Main entry point to doboz-web.
"""
from core.components.connectors.serial.queuable_serial import *
from core.components.hardware_nodes.reprap.reprap_node import ReprapNode
from core.components.hardware_nodes.webcam.webcam_node import WebcamNode
from core.print_server.print_server import *

import ConfigParser
import logging
import os
import socket


   

def configure_all():
    """
    Setup all pre required elements for reprap , webcam handling and webserver 
    """ 
    Config = ConfigParser.ConfigParser()
    rootPath = os.path.abspath(".")
    Config.read(os.path.join(rootPath, "config.cfg"))
    """"""""""""""""""""""""""""""""""""

    
    logger = logging.getLogger("Doboz.core")
    logger.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.ERROR)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    """"""""""""""""""""""""""""""""""""
    """Reprap config elements"""
    reprapNode = ReprapNode()
    qs = QSerial(seperator="\r\n", isBuffering=True, Speed=19200)
    reprapNode.set_connector(qs)
    reprapNode.start()
    
    """"""""""""""""""""""""""""""""""""
    """WebCam config elements"""
    useWebcam = Config.getboolean("WebCam", "use")
    webcamDriver = Config.get("WebCam", "driver")
    
    if useWebcam:
         from core.components.connectors.webcam.gstreamer_cam import GStreamerCam
         testBottle.webcamsEnabled = useWebcam
         webcamNode = WebcamNode()
         webcamNode.filePath = os.path.join(rootPath, "core", "print_server", "files", "static", "img", "test")
         webcamConnector = GStreamerCam(driver=webcamDriver)
         webcamNode.set_connector(webcamConnector)
         webcamNode.start()
         """"""
         testBottle.webcam = webcamNode

    """"""""""""""""""""""""""""""""""""
    """Web Server config elements"""
   
    server = server = Config.get("WebServer", "server")
    port = Config.getint("WebServer", "port")
    testBottle.chosenServer = server
    testBottle.chosenPort = port
    testBottle.reprapManager = reprapNode

def start_server():
    """
    starts all server components
    """
    start_webServer()
        
if __name__ == "__main__":
    configure_all()
    start_server()



