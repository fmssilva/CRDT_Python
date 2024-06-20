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
######################  COUNTRY PK  ###########################

class CountryPK(PK):
    '''Primary Key for the Country class. 
        We implement name as Int for better performance in Z3.'''

    def __init__(self, name: Int):
        super().__init__([name])
        self.name = name

    def reachable(self) -> BoolRef:
        '''If PK attributes have some CHECK constraints, they should be implemented here. Otherwise, return True.'''
        return True
   
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of CountryPK, and also list of those variables to be used by Z3.'''
        return PK.getArgs("countryPK_" + extra_id, ["name_"])
    


##############################################################
######################  ART   ELEM  ##########################

class Country(Element, CvRDT['Country']):
    '''A class to represent an Art.'''

    number_of_FKs = 0
    '''Number of foreign keys in this class. static, common to all instances of the class.'''
    
    def __init__(self, countryPK: 'CountryPK'):
        super().__init__([countryPK])
        self.countryPK = countryPK

    def reachable(self) -> BoolRef:
        return And(
            self.countryPK.reachable())
    
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of Country, and also list of those variables to be used by Z3.'''
        return Element.getArgs("country_"+extra_id, {"countryPK_": CountryPK})


##############################################################
######################  COUNTRY  TABLE  ##########################


class CountriesTable(DWTable):
    '''ArtsTable extends DWTable.'''
    
    def __init__(self, elements: Dict[CountryPK, Tuple[DWFlags, Country]], before: Callable[[Time, Time], bool]):
        super().__init__(elements, before)

    def getNumFKs(self) -> int:
        return Country.number_of_FKs
        
    @staticmethod
    def getArgs(extra_id: str, table_size: int, clock: Time):
        '''return symbolic all different variables for 3 different instances of CountriesTable, and also list of those variables to be used by Z3.'''
        return DWTable.getArgs("countriesTab_" + extra_id, Country, table_size, clock)
    


##############################################################
###################  ART  FK_SYSTEM  #########################

''' Art has no foreign keys.'''
