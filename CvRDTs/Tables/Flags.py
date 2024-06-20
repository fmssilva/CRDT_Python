

from z3 import *
from typing import List

from CvRDTs.CvRDT import CvRDT


class Status:
    DELETED = 0
    VISIBLE = 1


class Version:
    INIT_VERSION = 0
    ERROR_VERSION = -1



class Flags(CvRDT['Flags']):
    ''' Flags is a CvRDT that represents the flags of a table element.
       It has a version, a flag and a list of foreign keys versions.
       It extends CvRDT which accepts a generic type T, which we here bind to Flags.'''

    def __init__(self, version: int, flag: int):
        self.version = version
        self.flag = flag

    def compatible(self, that: 'Flags') -> BoolRef:
        return True
    

