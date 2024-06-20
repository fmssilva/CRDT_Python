
from z3 import *
from typing import Callable, Dict, Tuple

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.Time import Time
from CvRDTs.Registers.LWWRegister import LWWRegister

from CvRDTs.Tables.PK import PK
from CvRDTs.Tables.Element import Element
from CvRDTs.Tables.DWFlags import DWFlags
from CvRDTs.Tables.DWTable import DWTable



###############################################################
######################  Song PK  ###############################

class SongPK(PK):
    '''Primary Key for the Song class. 
        We implement title as Int for better performance in Z3.'''
        
    def __init__(self, title: Int):
        super().__init__([title])
        self.title = title

    def reachable(self) -> BoolRef:
        '''If PK attributes have some CHECK constraints, they should be implemented here. Otherwise, return True.'''
        return True
        
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of AlbPK, and also list of those variables to be used by Z3.'''
        return PK.getArgs("songPK_"+ extra_id, ["title_"])



##############################################################
######################  SONG   ELEM  #########################

class Song(Element, CvRDT['Song']):
    '''A class to represent an Song.'''

    number_of_FKs = 0
    '''Number of foreign keys in this class. static, common to all instances of the class.'''
    
    def __init__(self, songPK: 'SongPK', duration: 'LWWRegister[Int]', key_words: 'LWWRegister[Int]'):
        super().__init__([songPK, duration, key_words])
        self.songPK = songPK
        self.duration = duration
        self.key_words = key_words

    def reachable(self) -> BoolRef:
        return And(
            self.songPK.reachable(), 
            self.duration.value > 0)

    @staticmethod
    def getArgs(extra_id:str):
        '''return symbolic all different variables for 3 different instances of Alb, and also list of those variables to be used by Z3.'''
        return Element.getArgs("song_" + extra_id, {"songPK_": SongPK, "duration_": LWWRegister, "key_words_": LWWRegister})


##############################################################
######################  SONG  TABLE  ##########################


class SongsTable(DWTable):
    '''SongsTable extends DWTable.'''

    def __init__(self, elements: Dict[SongPK, Tuple[DWFlags, Song]], before: Callable[[Time, Time], bool],):
        super().__init__(elements, before)

    def getNumFKs(self) -> int:
        return Song.number_of_FKs

    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of SongsTable, and also list of those variables to be used by Z3.'''
        return DWTable.getArgs(extra_id + "songsTab_", Song)



##############################################################
###################  SONG  FK_SYSTEM  #########################

