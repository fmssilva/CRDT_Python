
from z3 import *

from typing import Callable, Dict, Tuple

from CvRDTs.Time.Time import Time
from CvRDTs.Tables.DWFlags import DWFlags
from CvRDTs.Tables.DWTable import DWTable
from ConcreteTables.Art import Art, ArtPK


class ArtsTable(DWTable[ArtPK, Art]):
    '''ArtsTable extends DWTable. DWTable accepts a generic type PK and V, which we here bind to ArtPK and Art.'''
    
    def __init__(self, elements: Dict[ArtPK, Tuple[DWFlags, Art]], before: Callable[[Time, Time], bool]):
        super().__init__(elements, before)

    def copy(self, newElements: Dict[ArtPK, Tuple[DWFlags, Art]]) -> 'ArtsTable':
        return ArtsTable(newElements, self.before)

    def getNumFKs(self) -> int:
        return Art.number_of_FKs
    
    
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of ArtsTable, and also list of those variables to be used by Z3.'''
        return DWTable.getArgs(extra_id+"ArtsTab", Art)
    