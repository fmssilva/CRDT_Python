from z3 import *

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Registers.LWWRegister import LWWRegister


###########################################################################################
###################################  ART PK  ##############################################

class ArtPK:
    '''Primary Key for the Art class. It has only one attribute: name.
        We implement name as Int for better performance in Z3.'''

    def __init__(self, name: Int):
        self.name = name

    def reachable(self) -> BoolRef:
        return True

    def equals(self, other: 'ArtPK') -> BoolRef:
        return self.name == other.name
    
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of ArtPK, and also list of those variables to be used by Z3.'''
        
        # symbolic varibales for 3 different instances of ArtPK
        name1, name2, name3 = Ints('name1%s name2%s name3%s' % (extra_id, extra_id, extra_id))

        artPK1_args = [name1]
        artPK2_args = [name2]
        artPK3_args = [name3]

        z3_vars_for_1_instance = [name1]
        z3_vars_for_2_instances = [name1, name2]
        z3_vars_for_3_instances = [name1, name2, name3]

        return artPK1_args, artPK2_args, artPK3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
    


###########################################################################################
###################################  ART  #################################################

class Art(CvRDT['Art']):
    '''A class to represent an Art. It has 2 attributes: artPK and age.'''

    number_of_FKs = 0
    '''Number of foreign keys in this class. static, common to all instances of the class.'''
    
    def __init__(self, artPK: 'ArtPK', age: 'LWWRegister[Int]'):
        self.artPK = artPK
        self.age = age

    def reachable(self) -> BoolRef:
        return And(
            self.artPK.reachable(),
            self.age.value >= 0, self.age.value <= 100)

    def equals(self, other: 'Art') -> BoolRef:
        return And(
            self.artPK.equals(other.artPK),
            self.age.equals(other.age))

    def compare(self, other: 'Art') -> BoolRef:
        # TODO - mas não é preciso porque fazemos override ao equals
        return False

    def compatible(self, other) -> BoolRef:
        return And(
            self.artPK.equals(other.artPK),
            self.age.compatible(other.age)
        )

    def merge(self, other: 'Art') -> 'Art':
        return Art(
            self.artPK,
            self.age.merge(other.age)
        )


    def getPK(self) -> 'ArtPK':
        return self.artPK

    
    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of Art, and also list of those variables to be used by Z3.'''

        # symbolic varibales for 3 different instances of Art
        artPK1_args, artPK2_args, artPK3_args, artPK_vars_for_1_instance, artPK_vars_for_2_instances, artPK_vars_for_3_instances = ArtPK.getArgs(extra_id+"artPK")
        age1_args, age2_args, age3_args, age_vars_for_1_instance, age_vars_for_2_instances, age_vars_for_3_instances = LWWRegister.getArgs(extra_id+"age")

        art1_args = [ArtPK(*artPK1_args), LWWRegister(*age1_args)]
        art2_args = [ArtPK(*artPK2_args), LWWRegister(*age2_args)]
        art3_args = [ArtPK(*artPK3_args), LWWRegister(*age3_args)]

        z3_vars_for_1_instance = artPK_vars_for_1_instance + age_vars_for_1_instance
        z3_vars_for_2_instances = artPK_vars_for_2_instances + age_vars_for_2_instances
        z3_vars_for_3_instances = artPK_vars_for_3_instances + age_vars_for_3_instances

        return art1_args, art2_args, art3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances