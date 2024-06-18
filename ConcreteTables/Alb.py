
from z3 import *

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Tables.PK import PK
from CvRDTs.Tables.Element import Element

from ConcreteTables.Art import ArtPK
from CvRDTs.Registers.LWWRegister import LWWRegister

###########################################################################################
###########################  ALBPK  #######################################################

class AlbPK(PK):
    
    number_of_FKs = 1

    def __init__(self, title: Int):
        self.title = title

    def reachable(self) -> BoolRef:
        return True
    
    def equals(self, other: 'AlbPK') -> BoolRef:
        if isinstance(other, ArtPK):
            return self.title == other.title
        return False
    
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of AlbPK, and also list of those variables to be used by Z3.'''
        return PK.getArgs("albPK_"+ extra_id, ["title"])

###########################################################################################
###################################  ALB  #################################################

class Alb(Element, CvRDT['Alb']):
    '''A class to represent an Alb. It has 3 attributes: albPK, artFK, year and price.'''

    number_of_FKs = 1
    '''Number of foreign keys in this class. static, common to all instances of the class.'''
    
    def __init__(self, albPK: 'AlbPK', artFK: 'ArtPK', year: 'LWWRegister[Int]', price: 'LWWRegister[Int]'):
        super().__init__([albPK, artFK, year, price])
        self.albPK = albPK
        self.artFK = artFK
        self.year = year
        self.price = price

    def reachable(self) -> BoolRef:
        return And(
            self.albPK.reachable(), self.artFK.reachable(),
            1900 <= self.year.value,
            self.year.value <= 2022 ,
            self.price.value >= 0, 
            self.price.value <= 10000)


    @staticmethod
    def getArgs(extra_id:str):
        '''return symbolic all different variables for 3 different instances of Alb, and also list of those variables to be used by Z3.'''
        return Element.getArgs("alb_"+extra_id, {"albPK": AlbPK, "artFK": ArtPK, "year": LWWRegister, "price": LWWRegister})
