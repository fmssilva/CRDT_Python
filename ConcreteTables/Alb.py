
from z3 import *

from ConcreteTables.Art import ArtPK
from CvRDTs.CvRDT import CvRDT
from CvRDTs.Registers.LWWRegister import LWWRegister

###########################################################################################
###########################  ALBPK  #######################################################

class AlbPK:
    
    number_of_FKs = 1

    def __init__(self, title: Int):
        self.title = title

    def reachable(self) -> bool:
        return True
    
    def equals(self, other: 'AlbPK') -> BoolRef:
        if isinstance(other, ArtPK):
            return self.title == other.title
        return False
    
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of AlbPK, and also list of those variables to be used by Z3.'''
        
        # symbolic varibales for 3 different instances of AlbPK
        title1, title2, title3 = Ints('title1%s title2%s title3%s' % (extra_id, extra_id, extra_id))
        
        albPK1_args = [title1]
        albPK2_args = [title2]
        albPK3_args = [title3]
        
        z3_vars_for_1_instance = [title1]
        z3_vars_for_2_instances = [title1, title2]
        z3_vars_for_3_instances = [title1, title2, title3]
        
        return albPK1_args, albPK2_args, albPK3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances



###########################################################################################
###################################  ALB  #################################################

class Alb(CvRDT['Alb']):
    '''A class to represent an Alb. It has 3 attributes: albPK, artFK, year and price.'''

    number_of_FKs = 1
    '''Number of foreign keys in this class. static, common to all instances of the class.'''
    
    def __init__(self, albPK: 'AlbPK', artFK: 'ArtPK', year: 'LWWRegister[Int]', price: 'LWWRegister[Int]'):
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

    def equals(self, other: 'Alb') -> BoolRef:
        return And(
            self.albPK.equals(other.albPK),
            self.artFK.equals(other.artFK),
            self.year.equals(other.year),
            self.price.equals(other.price))

    def compare(self, other: 'Alb') -> BoolRef:
        # TODO - mas não é preciso porque fazemos override ao equals
        return False
    
    def compatible(self, other: 'Alb') -> BoolRef:
        return And(
            self.albPK.equals(other.albPK),
            self.artFK.equals(other.artFK),
            self.year.compatible(other.year),
            self.price.compatible(other.price))

    def merge(self, other: 'Alb') -> 'Alb':
        return Alb(
            self.albPK, 
            self.artFK, 
            self.year.merge(other.year), 
            self.price.merge(other.price))

    def getPK(self) -> 'AlbPK':
        return self.albPK

    @staticmethod
    def getArgs(extra_id:str):
        '''return symbolic all different variables for 3 different instances of Alb, and also list of those variables to be used by Z3.'''
        
        # symbolic varibales for 3 different instances of Alb
        albPK1_args, albPK2_args, albPK3_args, albPK_vars_for_1_instance, albPK_vars_for_2_instances, albPK_vars_for_3_instances = AlbPK.getArgs(extra_id+"albPK")
        artFK1_args, artFK2_args, artFK3_args, artFK_vars_for_1_instance, artFK_vars_for_2_instances, artFK_vars_for_3_instances = ArtPK.getArgs(extra_id+"artFK")
        year1_args, year2_args, year3_args, year_vars_for_1_instance, year_vars_for_2_instances, year_vars_for_3_instances = LWWRegister.getArgs(extra_id+"year")
        price1_args, price2_args, price3_args, price_vars_for_1_instance, price_vars_for_2_instances, price_vars_for_3_instances = LWWRegister.getArgs(extra_id+"price")

        alb1_args =[AlbPK(*albPK1_args), ArtPK(*artFK1_args), LWWRegister(*year1_args), LWWRegister(*price1_args)]
        alb2_args =[AlbPK(*albPK2_args), ArtPK(*artFK2_args), LWWRegister(*year2_args), LWWRegister(*price2_args)]
        alb3_args =[AlbPK(*albPK3_args), ArtPK(*artFK3_args), LWWRegister(*year3_args), LWWRegister(*price3_args)]

        z3_vars_for_1_instance = albPK_vars_for_1_instance + artFK_vars_for_1_instance + year_vars_for_1_instance + price_vars_for_1_instance
        z3_vars_for_2_instances = albPK_vars_for_2_instances + artFK_vars_for_2_instances + year_vars_for_2_instances + price_vars_for_2_instances
        z3_vars_for_3_instances = albPK_vars_for_3_instances + artFK_vars_for_3_instances + year_vars_for_3_instances + price_vars_for_3_instances

        return alb1_args, alb2_args, alb3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances

        