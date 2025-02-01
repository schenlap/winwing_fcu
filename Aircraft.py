from abc import ABC, abstractmethod
from enum import Enum

class DREF_TYPE(Enum):
    DATA = 0
    CMD = 1
    NONE = 2 # for testing

class DREF():
    def __init__(self, label, dref, dreftype):
        self.label = label
        self.dref = dref
        self.dreftype = dreftype

class Aircraft(ABC):
    @abstractmethod
    def set_name(self, name): raise NotImplementedError

    @abstractmethod
    def create_aircraft(self): raise NotImplementedError
