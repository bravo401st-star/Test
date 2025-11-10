import inspect
import GameCore as gc
from collections.abc import Callable

class Event():
    def __init__(self, T: type = None):
        self.subscribers = []
        self.T = T


    def Trigger(self, param = None):
        if self.T != None:
            for func in self.subscribers:
                if ((type(param) == self.T or issubclass(type(param), self.T)) and len(inspect.signature(func).parameters) >= 1):
                    func(param)
            return

        for func in self.subscribers:
            func()


    def Subscribe(self, func):
        if func in self.subscribers:
            return
        
        self.subscribers.append(func)


    def Unsubscribe(self, func):
        if func in self.subscribers == False:
            return
        
        self.subscribers.remove(func)