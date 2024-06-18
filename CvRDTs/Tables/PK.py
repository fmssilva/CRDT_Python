
from z3 import *

from typing import List

class PK:
    ''' generic class for Primary Keys to extend.
        For better efficiency, we implement all attributes of the PK as Ints in Z3.'''
    
    # TODO: if we want to accept multiple data types we can receive a dict: attrib_name -> attrib_type, similar to Element Class
    @staticmethod
    def getArgs(extra_id: str, args: List[str]):
        '''return symbolic all different variables for 3 different instances of the given concrete PK, 
            and also list of those variables to be used by Z3.'''
        
        pk1_args, pk2_args, pk3_args = [], [], []
        
        # symbolic varibales for 3 different instances of the given concrete PK
        for arg in args:
            pk1_args.append(Int(f'{arg}1_{extra_id}'))
            pk2_args.append(Int(f'{arg}2_{extra_id}'))
            pk3_args.append(Int(f'{arg}3_{extra_id}'))

        z3_vars_for_1_instance = pk1_args
        z3_vars_for_2_instances = pk1_args + pk2_args
        z3_vars_for_3_instances = pk1_args + pk2_args + pk3_args

        return pk1_args, pk2_args, pk3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
    