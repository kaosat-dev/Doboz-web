import os
import socket




from Core.connectors.Serial.queuable_serial import * 
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
qs=QSerial(seperator="\r\n",isBuffering=True,Speed=19200)
reprapNode.set_connector(qs)

testBottle.reprapManager=reprapNode

start_webServer()


