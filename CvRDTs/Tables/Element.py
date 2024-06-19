
from z3 import *

from typing import Dict, List, TypeVar

from CvRDTs.Tables.PK import PK

T = TypeVar('T')

class Element:
    ''' generic class for Elements to extend.
        For better efficiency, we implement all attributes of the Element as Ints in Z3.'''

    def __init__(self, elem_args):
        self.elem_args = elem_args


    def equals(self, other: 'Element') -> BoolRef:
        '''return the equality of the given Element with the current Element.'''
        return And(*[thisArg.equals(thatArg) for thisArg, thatArg in zip (self.elem_args, other.elem_args)])

    def __eq__(self, other: 'Element') -> BoolRef:
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.'''
        return And(*[thisArg.pure_equals(thatArg) for thisArg, thatArg in zip (self.elem_args, other.elem_args)])

    def compare(self, other: 'Element') -> BoolRef:
        # TODO - mas não é preciso porque fazemos override ao equals
        return False


    def compatible(self, other: 'Element') -> BoolRef:
        '''return the compatibility of the given Element with the current Element.'''
        booleans = []
        for thisArg, thatArg in zip(self.elem_args, other.elem_args):
            if isinstance(thisArg, PK): # PKs and FKs must be equal
                booleans.append(thisArg.equals(thatArg))
            else:
                booleans.append(thisArg.compatible(thatArg))
        return And(*booleans)


    def merge(self, other: 'Element') -> 'Element':
        '''return the merge of the given Element with the current Element.'''
        merged_args = []
        for thisArg, thatArg in zip(self.elem_args, other.elem_args):
            if isinstance(thisArg, PK): # PKs and FKs must be equal so we just take the first one
                merged_args.append(thisArg)
            else:
                merged_args.append(thisArg.merge(thatArg))
        return type(self)(*merged_args)
    
    def getPK(self):
        '''return the Primary Key of the Element.
            @Pre: the first attribute of the Element must be the Primary Key.'''
        return self.elem_args[0]


    @staticmethod
    def getArgs(extra_id: str, args: Dict[str, T]):
        '''return symbolic all different variables for 3 different instances of the given concrete Element, 
            and also list of those variables to be used by Z3.'''
        
        elem1_args, elem2_args, elem3_args = [], [], []
        z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances = [], [], []

        # symbolic variables for 3 different instances of each attribute of the given concrete Element
        for attrib_name, attrib_type in args.items():
            # getArgs of the attribute class
            att1_args, att2_args, att3_args, att_vars_for_1_instance, att_vars_for_2_instances, att_vars_for_3_instances = attrib_type.getArgs(attrib_name + extra_id)
            
            # create an instance of the attribute and add to args the Element
            elem1_args.append(attrib_type(*att1_args)) # Element, like Album, has atributes which are object like (albPK: AlbPK, artFK: ArtPK, price: LWWRegister)... 
            elem2_args.append(attrib_type(*att2_args)) # so here we are creating those objects with the given arguments like, and adding them to the list of arguments of the Element
            elem3_args.append(attrib_type(*att3_args)) # a similar concrete implementation is: AlbPK(*albPK1_args), or ArtPK(*artFK1_args), or LWWRegister(*year1_args), or LWWRegister(*price1_args)...

            # add the symbolic variables of the attribute to the list of symbolic variables of the Element
            z3_vars_for_1_instance.extend(att_vars_for_1_instance)
            z3_vars_for_2_instances.extend(att_vars_for_2_instances)
            z3_vars_for_3_instances.extend(att_vars_for_3_instances)

        return elem1_args, elem2_args, elem3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances

