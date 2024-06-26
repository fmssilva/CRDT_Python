
from abc import abstractmethod
from z3 import *

from typing import Dict, List, TypeVar

from CvRDTs.Tables.PK import PK

T = TypeVar('T')

class Element:
    ''' generic class for Elements to extend.
        For better efficiency, we implement all attributes of the Element as Ints in Z3.'''

    def __init__(self, elem_args):
        self.elem_args = elem_args

    def compatible(self, other: 'Element') -> BoolRef:
        '''return the compatibility of the given Element with the current Element.'''
        booleans = []
        # we use zip to enforce that each arg is in the same position in both elements
        for thisArg, thatArg in zip(self.elem_args, other.elem_args):
            if isinstance(thisArg, PK): # PKs and FKs must be equal
                booleans.append(thisArg.equals(thatArg))
            else:
                booleans.append(thisArg.compatible(thatArg))
        return And(*booleans)
    
    @abstractmethod
    def reachable(self) -> BoolRef:
        '''Each Element must verify the CHECK constraints of its concrete attributes.'''
        pass

    def __eq__(self, other: 'Element') -> BoolRef:
        ''' Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.
            @Pre: self.compatible(other)'''
            # we use zip to enforce that each arg is in the same position in both elements
        return And(*[thisArg.__eq__(thatArg) for thisArg, thatArg in zip (self.elem_args, other.elem_args)])
    
    def equals(self, other: 'Element') -> BoolRef:
        ''' return the equality of the given Element with the current Element.
            @Pre: self.compatible(other)'''
            # we use zip to enforce that each arg is in the same position in both elements
        return And(*[thisArg == thatArg for thisArg, thatArg in zip (self.elem_args, other.elem_args)])

    def compare(self, other: 'Element') -> BoolRef:
        '''return the comparison of the given Element with the current Element.'''
        # TODO - but we are overriding equals, so we don't need this method
        return False
    

    def merge(self, other: 'Element') -> 'Element':
        '''return the merge of the given Element with the current Element.
            @Pre: self.compatible(other)'''
        merged_args = []
            # we use zip because we know self.compatible(other) and so we know each arg is in the right position of the list
        for thisArg, thatArg in zip(self.elem_args, other.elem_args):
            if isinstance(thisArg, PK): # PKs and FKs must be equal so we just take the first one
                merged_args.append(thisArg)
            else:
                merged_args.append(thisArg.merge(thatArg))
        return self.__class__(*merged_args)
    
    def merge_with_version(self, other: 'Element', this_version: int, that_version: int) -> 'Element':
        '''return the merge of the given Element with the current Element, considering the versions of the Elements.'''
        merged_args = []
        for thisArg, thatArg in zip(self.elem_args, other.elem_args):
            if isinstance(thisArg, PK): # PKs and FKs must be equal so we just take the first one
                merged_args.append(thisArg)
            else: # merge the other attributes
                merged_args.append(thisArg.merge_with_version(thatArg, this_version, that_version))
        # TODO ???
        return self.__class__(*merged_args)


    def getPK(self):
        '''return the Primary Key of the Element.
            @Pre: the first attribute of the Element must be the Primary Key.'''
        return self.elem_args[0]


    @staticmethod
    def getArgs(extra_id: str, args: Dict[str, T]):
        '''return symbolic all different variables for 3 different instances of the given concrete Element, 
            and also list of those variables to be used by Z3.'''
        
        elem1_args, elem2_args, elem3_args = [], [], []
        z3_vars_for_instance1, z3_vars_for_instance2, z3_vars_for_instance3 = [], [], []

        # symbolic variables for 3 different instances of each attribute of the given concrete Element
        for attrib_name, attrib_type in args.items():
            # getArgs of the attribute class
            att1_args, att2_args, att3_args, att_vars_for_instance1, att_vars_for_instance2, att_vars_for_instance3 = attrib_type.getArgs(attrib_name + extra_id)
            
            # create an instance of the attribute and add to args the Element
            elem1_args.append(attrib_type(*att1_args)) # Element, like Album, has atributes which are object like (albPK: AlbPK, artFK: ArtPK, price: LWWRegister)... 
            elem2_args.append(attrib_type(*att2_args)) # so here we are creating those objects with the given arguments like, and adding them to the list of arguments of the Element
            elem3_args.append(attrib_type(*att3_args)) # a similar concrete implementation is: AlbPK(*albPK1_args), or ArtPK(*artFK1_args), or LWWRegister(*year1_args), or LWWRegister(*price1_args)...

            # add the symbolic variables of the attribute to the list of symbolic variables of the Element
            z3_vars_for_instance1.extend(att_vars_for_instance1)
            z3_vars_for_instance2.extend(att_vars_for_instance2)
            z3_vars_for_instance3.extend(att_vars_for_instance3)

        return elem1_args, elem2_args, elem3_args, z3_vars_for_instance1, z3_vars_for_instance2, z3_vars_for_instance3

