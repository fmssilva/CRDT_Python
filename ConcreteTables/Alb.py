
from z3 import *
from typing import Callable, Dict, Tuple

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.Time import Time
from CvRDTs.Registers.LWWRegister import LWWRegister

from CvRDTs.Tables.PK import PK
from CvRDTs.Tables.Element import Element
from CvRDTs.Tables.DWFlags import DWFlags
from CvRDTs.Tables.DWTable import DWTable
from CvRDTs.Tables.FK_System import FK_System

from ConcreteTables.Art import ArtPK, ArtsTable
from ConcreteTables.Song import SongPK



###############################################################
######################  ALB PK  ###############################

class AlbPK(PK):
    '''Primary Key for the Alb class. It has only one attribute: title.
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
        return PK.getArgs("albPK_"+ extra_id, ["title_"])



##############################################################
######################  ALB   ELEM  ##########################

class Alb(Element, CvRDT['Alb']):
    '''A class to represent an Alb.'''

    number_of_FKs = 4
    '''Number of foreign keys in this class. static, common to all instances of the class.'''
    
    def __init__(self, albPK: 'AlbPK', artFK: 'ArtPK', songA:'SongPK', songB:'SongPK', songC:'SongPK', year: 'LWWRegister[Int]', price: 'LWWRegister[Int]'):
        super().__init__([albPK, artFK, year, price])
        self.albPK = albPK
        self.artFK = artFK
        self.songA = songA
        self.songB = songB
        self.songC = songC
        self.year = year
        self.price = price

    def reachable(self) -> BoolRef:
        return And(
            self.albPK.reachable(), 
            self.artFK.reachable(),
            self.songA.reachable(), self.songB.reachable(), self.songC.reachable(),
            1900 <= self.year.value,
            self.year.value <= 2022 ,
            self.price.value >= 0, 
            self.price.value <= 10000)

    @staticmethod
    def getArgs(extra_id:str):
        '''return symbolic all different variables for 3 different instances of Alb, and also list of those variables to be used by Z3.'''
        return Element.getArgs("alb_" + extra_id, {"albPK_": AlbPK, "artFK_": ArtPK, "songA_": SongPK, "songB_": SongPK, "songC_": SongPK, 
                                                   "year_": LWWRegister, "price_": LWWRegister})


##############################################################
######################  ALB  TABLE  ##########################


class AlbsTable(DWTable):
    '''AlbsTable extends DWTable.'''

    def __init__(self, elements: Dict[AlbPK, Tuple[DWFlags, Alb]], before: Callable[[Time, Time], bool],):
        super().__init__(elements, before)

    def getNumFKs(self) -> int:
        return Alb.number_of_FKs

    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of AlbsTable, and also list of those variables to be used by Z3.'''
        return DWTable.getArgs(extra_id + "albsTab_", Alb)



##############################################################
###################  ALB  FK_SYSTEM  #########################


class Alb_FK_System(FK_System):
    '''A class to represent an Alb_FK_System. It has 2 attributes: albs_table and arts_table.
        Extends CvRDT, and CvRDT accepts a generic type T, which we here bind to Alb_FK_System.'''
         
    def __init__(self, albs_table: AlbsTable, arts_table: ArtsTable):
        super().__init__(albs_table, [arts_table], [])
        self.albs_table = albs_table
        self.arts_table = arts_table

   
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of Alb_FK_System, and also list of those variables to be used by Z3.'''
        return FK_System.getArgs("albFKsyst_" + extra_id, {"albTab_": AlbsTable, "artTab_": ArtsTable})
      

    @staticmethod
    def get_RefIntProof_Args(extra_id: str):
        '''return symbolic all different variables for 2 different instances of Alb_FK_System and 1 instance of AlbPK, and also list of those variables to be used by Z3.'''
        return FK_System.get_RefIntProof_Args(extra_id, Alb_FK_System, AlbPK)
        
