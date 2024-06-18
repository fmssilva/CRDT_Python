
from z3 import *

from typing import Callable, Dict, Tuple

from CvRDTs.Time.Time import Time
from CvRDTs.Tables.DWFlags import DWFlags
from CvRDTs.Tables.DWTable import DWTable
from ConcreteTables.Alb import Alb, AlbPK



class AlbsTable(DWTable[AlbPK, Alb]):
    '''AlbsTable extends DWTable. DWTable accepts a generic type PK and V, which we here bind to AlbPK and Alb.'''

    def __init__(self, elements: Dict[AlbPK, Tuple[DWFlags, Alb]], before: Callable[[Time, Time], bool],):
        super().__init__(elements, before)

    def copy(self, newElements: Dict[AlbPK, Tuple[DWFlags, Alb]]) -> 'AlbsTable':
        return AlbsTable(newElements, self.before)

    def getNumFKs(self) -> int:
        return Alb.number_of_FKs

    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of AlbsTable, and also list of those variables to be used by Z3.'''
        return DWTable.getArgs(extra_id+"AlbsTab", Alb)

