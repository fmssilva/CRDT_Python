

from abc import abstractmethod
from z3 import *
from typing import List

from z3 import BoolRef

from CvRDTs.CvRDT import CvRDT


class Status:
    DELETED = 0
    VISIBLE = 1
    TOUCHED = 2
    NOT_TOUCHED = 3


class Version:
    INIT_VERSION = 0
    ERROR_VERSION = -1



class Flags(CvRDT['Flags']):
    ''' Flags is a CvRDT that represents the flags of a table element.
       It has a version, a flag and a list of foreign keys versions.
       It extends CvRDT which accepts a generic type T, which we here bind to Flags.'''

    def __init__(self, DI_flag: int):
        self.DI_flag = DI_flag
    
    @abstractmethod
    def equals(self, that: 'Flags') -> BoolRef:
        pass

    def compare(self, that: 'Flags') -> BoolRef:
        ''' we override equals from CvRDT so this is not used'''
        return False


