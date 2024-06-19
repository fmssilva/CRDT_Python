from typing import Callable, Dict, Tuple
from z3 import *

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.Time import Time

from CvRDTs.Tables.PK import PK
from CvRDTs.Tables.Element import Element
from CvRDTs.Tables.DWFlags import DWFlags
from CvRDTs.Tables.DWTable import DWTable
from CvRDTs.Registers.LWWRegister import LWWRegister



###############################################################
######################  ART PK  ###############################

class ArtPK(PK):
    '''Primary Key for the Art class. It has only one attribute: name.
        We implement name as Int for better performance in Z3.'''

    def __init__(self, name: Int):
        super().__init__([name])
        self.name = name

    def reachable(self) -> BoolRef:
        '''If PK attributes have some CHECK constraints, they should be implemented here. Otherwise, return True.'''
        return True
   
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of ArtPK, and also list of those variables to be used by Z3.'''
        return PK.getArgs("artPK_" + extra_id, ["name_"])
    


##############################################################
######################  ART   ELEM  ##########################

class Art(Element, CvRDT['Art']):
    '''A class to represent an Art. It has 2 attributes: artPK and age.'''

    number_of_FKs = 0
    '''Number of foreign keys in this class. static, common to all instances of the class.'''
    
    def __init__(self, artPK: 'ArtPK', age: 'LWWRegister[Int]'):
        super().__init__([artPK, age])
        self.artPK = artPK
        self.age = age

    def reachable(self) -> BoolRef:
        return And(
            self.artPK.reachable(),
            self.age.value >= 0, self.age.value <= 100)
    
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of Art, and also list of those variables to be used by Z3.'''
        return Element.getArgs("art_"+extra_id, {"artPK_": ArtPK, "age_": LWWRegister})


##############################################################
######################  ART  TABLE  ##########################


class ArtsTable(DWTable):
    '''ArtsTable extends DWTable.'''
    
    def __init__(self, elements: Dict[ArtPK, Tuple[DWFlags, Art]], before: Callable[[Time, Time], bool]):
        super().__init__(elements, before)

    def copy(self, newElements: Dict[ArtPK, Tuple[DWFlags, Art]]) -> 'ArtsTable':
        return ArtsTable(newElements, self.before)

    def getNumFKs(self) -> int:
        return Art.number_of_FKs
        
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of ArtsTable, and also list of those variables to be used by Z3.'''
        return DWTable.getArgs("artsTab_" + extra_id, Art)
    


##############################################################
###################  ART  FK_SYSTEM  #########################

''' Art has no foreign keys.'''
