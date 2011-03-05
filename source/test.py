import os
import socket


from Core.print_server.print_server import *

logger=logging.getLogger("Doboz.Core")
logger.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.ERROR)
ch.setFormatter(formatter)
logger.addHandler(ch)
    
reprapManager=ReprapManager()
reprapManager.set_paths(os.path.join(os.path.abspath("."),"Core","print_server","files","machine"))
reprapManager.init()    
testBottle.reprapManager=reprapManager
testBottle.lineparseEventRecieved=False
testBottle.lastRecievedLine=""



start_webServer()