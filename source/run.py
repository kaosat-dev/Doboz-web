import os
import socket
import logging



from Core.connectors.serial.queuable_serial import * 
from Core.connectors.webcam.gstreamer_cam import * 

from Core.hardwareNodes.reprap.reprap_node import ReprapNode
from Core.hardwareNodes.webcam.webcam_node import WebcamNode
from Core.print_server.print_server import *

logger=logging.getLogger("Doboz.Core")
logger.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.ERROR)
ch.setFormatter(formatter)
logger.addHandler(ch)


reprapNode=ReprapNode()
webcamNode=WebcamNode()
webcamNode.filePath=os.path.join(os.path.abspath("."),"Core","print_server","files","static","img","test")

qs=QSerial(seperator="\r\n",isBuffering=True,Speed=19200)
gsc=GStreamerCam()

reprapNode.set_connector(qs)
webcamNode.set_connector(gsc)

webcamNode.start()

testBottle.reprapManager=reprapNode



start_webServer()


