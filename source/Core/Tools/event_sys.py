# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="ckaos"
__date__ ="$23 nov. 2009 16:22:12$"

class Events:
    def __getattr__(self, name):
      if hasattr(self.__class__, '__events__'):
         assert name in self.__class__.__events__, \
                "Event '%s' is not declared" % name
      self.__dict__[name] = ev = EventSlot(name)
      return ev

    def __repr__(self): return 'Events' + str(list(self))
    __str__ = __repr__
    def __len__(self): return NotImplemented
    def __iter__(self):
      def gen(dictitems=self.__dict__.items()):
         for attr, val in dictitems:
            if isinstance(val, EventSlot):
               yield val
      return gen()


class EventSlot():
    def __init__(self,name):
        self.handlers=[]
        self.__name__=name

    def __iadd__(self,handler):
        self.handlers.append(handler)
        return self

    def __isub__(self,handler):
        for handl in self.handlers:
            self.handlers.remove(handl)
        return self

    def __call__(self,*a,**kw):
        for handler in self.handlers:
            handler(*a,**kw)
    