from pollapli.core.tools.event_sys import *


class ConditionEvents(Events):
    """
    Class defining events associated to HardwareConnector Class
    """
    __events__=('validated','invalidated')


class Condition(object):
    """A condition is similar to a boolean expression: it must return
    true or false in its call method """
    def __init__(self):
        self.events=ConditionEvents()
        
    def validate(self):
        self.events.validated(self)
    
    def invalidate(self):
        self.events.invalidated(self)