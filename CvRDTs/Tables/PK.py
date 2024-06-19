
from z3 import *

from typing import List

class PK:
    ''' generic class for Primary Keys to extend.
        For better efficiency in Z3, we implement all attributes of the PK as Ints.'''
    
    def __init__(self, pk_args: List[Int]):
        self.pk_args = pk_args
    
    def __eq__(self, other: 'PK') -> BoolRef:
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.'''
        return self.equals(other)

    def equals(self, other: 'PK') -> BoolRef:
        '''return the equality of the given PK with the current PK.'''
        if isinstance(other, self.__class__) and hasattr(other, 'pk_args'):
            return And(len(self.pk_args) == len(other.pk_args), 
                *[thisArg == thatArg for thisArg, thatArg in zip(self.pk_args, other.pk_args)])
        return False

    # TODO: if we want to accept multiple data types we can receive a dict: attrib_name -> attrib_type, similar to Element Class
    @staticmethod
    def getArgs(extra_id: str, pk_args: List[str]):
        '''return symbolic all different variables for 3 different instances of the given concrete PK, 
            and also list of those variables to be used by Z3.'''
        
        pk1_args, pk2_args, pk3_args = [], [], []
        
        # symbolic varibales for 3 different instances of the given concrete PK
        for arg in pk_args:
            pk1_args.append(Int(f'{arg}1_{extra_id}'))
            pk2_args.append(Int(f'{arg}2_{extra_id}'))
            pk3_args.append(Int(f'{arg}3_{extra_id}'))

        z3_vars_for_1_instance = pk1_args
        z3_vars_for_2_instances = pk1_args + pk2_args
        z3_vars_for_3_instances = pk1_args + pk2_args + pk3_args

        return pk1_args, pk2_args, pk3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
    