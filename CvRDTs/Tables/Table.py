
from typing import Callable, Dict, Tuple
from z3 import *

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Tables.DWFlags import DWFlags
from CvRDTs.Tables.Element import Element
from CvRDTs.Tables.PK import PK
from CvRDTs.Time.Time import Time


class Table(CvRDT['Table']): 
    ''' generic class for Delete Wins or Update Wins Tables to extend.'''

    def __init__(self, elements: Dict[PK, Tuple[DWFlags, Element]], before: Callable[[Time, Time], bool]): 
        self.elements = elements  # elements is a dict with PK as key and (DWFlags, V) as value
        self.before = before  # before is a function (Time, Time) => Bool
