
from z3 import *
from typing import Callable, Dict, Tuple

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.Time import Time
from CvRDTs.Registers.LWWRegister import LWWRegister

from CvRDTs.Tables.PK import PK
from CvRDTs.Tables.Element import Element
from CvRDTs.Tables.Flags_DW import Flags_DW
from CvRDTs.Tables.DWTable import DWTable



###############################################################
######################  GENRE PK  #############################

class GenrePK(PK):
    '''Primary Key for the Genre class. 
        We implement title as Int for better performance in Z3.'''
        
    def __init__(self, title: Int):
        super().__init__([title])
        self.title = title

    def reachable(self) -> BoolRef:
        '''If PK attributes have some CHECK constraints, they should be implemented here. Otherwise, return True.'''
        return True
        
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of GenrePK, and also list of those variables to be used by Z3.'''
        return PK.getArgs("genrePK_"+ extra_id, ["title_"])



##############################################################
######################  GENRE   ELEM  #########################

class Genre(Element, CvRDT['Genre']):
    '''A class to represent an Genre.'''

    number_of_FKs = 0
    '''Number of foreign keys in this class. static, common to all instances of the class.'''
    
    def __init__(self, genrePK: 'GenrePK', key_words: 'LWWRegister[Int]'):
        super().__init__([genrePK, key_words])
        self.genrePK = genrePK
        self.key_words = key_words

    def reachable(self) -> BoolRef:
        return And(
            self.genrePK.reachable(), 
            self.key_words.value > 0)

    @staticmethod
    def getArgs(extra_id:str):
        '''return symbolic all different variables for 3 different instances of Alb, and also list of those variables to be used by Z3.'''
        return Element.getArgs("genre_" + extra_id, {"genrePK": GenrePK, "key_words_": LWWRegister})


##############################################################
######################  GENRE  TABLE  ##########################


class GenreTable(DWTable):
    '''SongsTable extends DWTable.'''

    def __init__(self, elements: Dict[GenrePK, Tuple[Flags_DW, Genre]], before: Callable[[Time, Time], bool]):
        super().__init__(elements, before)

    def getNumFKs(self) -> int:
        return Genre.number_of_FKs

    @staticmethod
    def getArgs(extra_id: str, table_size: int, clock: Time):
        '''return symbolic all different variables for 3 different instances of SongsTable, and also list of those variables to be used by Z3.'''
        return DWTable.getArgs(extra_id + "genresTab_", Genre, table_size, clock)



##############################################################
###################  SONG  FK_SYSTEM  #########################

