from typing import Callable, Dict, Tuple
from z3 import *

from ConcreteTables.Country import CountriesTable, CountryPK
from ConcreteTables.Genre import GenrePK, GenreTable
from CvRDTs.CvRDT import CvRDT
from CvRDTs.Tables.FK_System import FK_System
from CvRDTs.Time.Time import Time

from CvRDTs.Tables.PK import PK
from CvRDTs.Tables.Element import Element
from CvRDTs.Tables.Flags_UW import Flags_UW
from CvRDTs.Tables.Table_UW import Table_UW
from CvRDTs.Registers.LWWRegister import LWWRegister



###############################################################
######################  ART PK  ###############################

class ArtPK(PK):
    '''Primary Key for the Art class. It has only one attribute: name.
        We implement name as Int for better performance in Z3.'''

    def __init__(self, name: Int, id: Int):
        super().__init__([name, id])

    def reachable(self) -> BoolRef:
        '''If PK attributes have some CHECK constraints, they should be implemented here. Otherwise, return True.'''
        return True
   
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of ArtPK, and also list of those variables to be used by Z3.'''
        return PK.getArgs("artPK_" + extra_id, ["name_", "id_"])
    


##############################################################
######################  ART   ELEM  ##########################

class Art(Element, CvRDT['Art']):
    '''A class to represent an Art. It has 2 attributes: artPK and age.'''

    number_of_FKs = 2
    '''Number of foreign keys in this class. static, common to all instances of the class.'''
    
    def __init__(self, artPK: 'ArtPK', genre:'GenrePK', country:'CountryPK', age: 'LWWRegister[Int]'):
        super().__init__([artPK, genre, country, age])
        self.artPK = artPK
        self.genre = genre
        self.country = country
        self.age = age

    def reachable(self) -> BoolRef:
        return And(
            self.artPK.reachable(),
            self.genre.reachable(),
            self.country.reachable(),
            self.age.value >= 0, self.age.value <= 100)
    
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of Art, and also list of those variables to be used by Z3.'''
        return Element.getArgs("art_"+extra_id, {"artPK_": ArtPK, "genre": GenrePK, "country": CountryPK, "age_": LWWRegister})


##############################################################
######################  ART  TABLE  ##########################


class ArtsTable(Table_UW):
    '''ArtsTable extends UWTable.'''
    
    def __init__(self, elements: Dict[ArtPK, Tuple[Flags_UW, Art]], before: Callable[[Time, Time], bool]):
        super().__init__(elements, before)

    def getNumFKs(self) -> int:
        return Art.number_of_FKs
        
    @staticmethod
    def getArgs(extra_id: str, table_size: int, clock: Time):
        '''return symbolic all different variables for 3 different instances of ArtsTable, and also list of those variables to be used by Z3.'''
        return Table_UW.getArgs("artsTab_" + extra_id, Art, table_size, clock)
    


##############################################################
###################  ART  FK_SYSTEM  #########################

class Art_FK_System(FK_System):
    '''A class to represent an Alb_FK_System. It has 2 attributes: albs_table and arts_table.
        Extends CvRDT, and CvRDT accepts a generic type T, which we here bind to Alb_FK_System.'''
    
    def __init__(self, arts_table: ArtsTable, genres_table: GenreTable, countries_table: CountriesTable):
        '''Important: the order of the args in the constructor should be the same as the order of the args
            - here passing to super as "main_table", [fk_tables], [fk_systems]
            - in the getArgs method to create this instances.'''
        super().__init__(arts_table, [genres_table, countries_table], [])

   
    @staticmethod
    def getArgs(extra_id: str, table_size: int, clock: Time):
        '''return symbolic all different variables for 3 different instances of Alb_FK_System, and also list of those variables to be used by Z3.'''
        return FK_System.getArgs("artFKsyst_" + extra_id, {"artTab_": ArtsTable, "genrTab_": GenreTable, "countrTab_":CountriesTable }, table_size, clock)
      

    @staticmethod
    def get_RefIntProof_Args(extra_id: str, table_size: int, clock: Time):
        '''return symbolic all different variables for 2 different instances of Alb_FK_System and 1 instance of AlbPK, and also list of those variables to be used by Z3.'''
        return FK_System.get_RefIntProof_Args(extra_id, Art_FK_System, ArtPK, table_size, clock)
        
