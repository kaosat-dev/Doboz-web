from threading import Thread 
import time
from Core.Tools.event_sys import *

class SimpleTimer(Thread): 
    """
    Simple timer that calls the callback function once the time is elapsed
    """
    def __init__(self,callback,delay,*args,**kwargs):
        self.callback=callback
        self.delay=delay
    
    
    def run(self):
        time.sleep(self.delay)
        self.callback()
        
class TimerEvents(Events):
    __events__=("Elapsed")   
        
def EventTimer(Thread):
    """
    Timer that raises an "Elapsed" event once the time is elapsed 
    """
    def __init__(self,delay,*args,**kwargs):

        self.delay=delay
        self.events=TimerEvents()

    def run(self):
        time.sleep(self.delay)
        self.events.Elapsed(self,None)
