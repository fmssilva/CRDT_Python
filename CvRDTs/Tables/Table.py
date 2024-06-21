
from abc import abstractmethod
from typing import Callable, Dict, Tuple
from z3 import *

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Tables.Flags import Flags, Status
from CvRDTs.Tables.Flags_DW import Flags_DW
from CvRDTs.Tables.Element import Element
from CvRDTs.Tables.PK import PK
from CvRDTs.Time.Time import Time


class Table(CvRDT['Table']): 
    ''' generic class for Delete Wins or Update Wins Tables to extend.'''

    def __init__(self, elements: Dict[PK, Tuple[Flags_DW, Element]], before: Callable[[Time, Time], bool]): 
        self.elements = elements  # elements is a dict with PK as key and (DWFlags, V) as value
        self.before = before  # before is a function (Time, Time) => Bool


    @abstractmethod
    def getNumFKs(self) -> int:
        pass

    def compatible(self, other: 'Table') -> BoolRef:
        '''for all elements in zip (this values(), that values()), check if they are compatible.
            (and to reduce search space for z3, we add some assumptions before)'''
        return And(
            self.before == other.before,
            # we use zip which iterate over the map without any order and without matching keys, but it's enough to check if the elements are compatible, they don't need to be the same one. And also if one table is bigger than the other, we don't need to check the rest of the elements.
            And(*[And(e1[0].compatible(e2[0]), e1[1].compatible(e2[1])) for (e1, e2) in zip(self.elements.values(), other.elements.values())])
        )
    
    
    def reachable(self) -> BoolRef : 
        '''for all elements in elements.values() check if they respect the conditions'''
        return And(*[And(   # check PK
                            pk.reachable(),
                            # check flags
                            elem[0].reachable(),
                            elem[0].DI_flag != Status.DELETED,
                            self.reachable_complement(elem[0]),
                            # check values
                            elem[1].reachable()
                        ) for pk, elem in self.elements.items()
                    ])

    def __eq__(self, other: 'Table') -> BoolRef:
        ''' Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.
            @Pre: self.compatible(other)'''
        booleans = []
        union_keys = set(self.elements.keys()).union(other.elements.keys())
        intersection_keys = set(self.elements.keys()).intersection(other.elements.keys())
        if len(union_keys) != len(intersection_keys):
            return False
        for pk in intersection_keys:
            e1 = self.elements[pk]
            e2 = other.elements[pk]
            booleans.append(And(e1[0] == e2[0], e1[1] == e2[1]))
        return And(And(*booleans), self.before == other.before)
    
    def equals(self, other: 'Table') -> BoolRef:
        ''' for all elements in zip (this values(), that values()), check if they are equal
            @Pre: self.compatible(other)'''
        union_keys = set(self.elements.keys()).union(other.elements.keys())
        intersection_keys = set(self.elements.keys()).intersection(other.elements.keys())
        if len(union_keys) != len(intersection_keys):
            return False
        booleans = []
        for pk in intersection_keys:
            e1 = self.elements[pk]
            e2 = other.elements[pk]
            booleans.append(And(e1[0].equals(e2[0]), e1[1].equals(e2[1])))
        return And(And(*booleans), self.before == other.before)
        
    def compare(self, other: 'Table') -> BoolRef:
        ''' Returns True if `self`<=`that`.
            for all elements in zip (this values(), that values()), check if they are comparable'''
        # TODO: same as equals but with method compare
        return False
    
    def copy (self, newElements: Dict[PK, Tuple[Flags, Element]]) -> 'Table':
        '''return a new DWTable with the given elements.'''
        return self.__class__(newElements, self.before)


    @staticmethod
    def getArgs(extra_id: str, elem: Element, table_size: int, clock: Time, flags: Flags):
        '''return symbolic all different variables for 3 different instances of a given concrete table, and also list of those variables to be used by Z3.'''

        vars_for_instance1, vars_for_instance2, vars_for_instance3 = [], [], []

        elements1, elements2, elements3 = {}, {}, {}
        for i in range(table_size):  
            elem1_args, elem2_args, elem3_args3, elem_vars_for_instance1, elem_args_for_instance2, elem_args_for_instance3 = elem.getArgs(str(i) + "_DWTab_" + extra_id)
            elem1, elem2, elem3 = elem(*elem1_args), elem(*elem2_args), elem(*elem3_args3)
        
            args_for_flags = [str(i) + "_DWTab_" + extra_id, elem.number_of_FKs] if flags == Flags_DW else [str(i) + "_DWTab_" + extra_id, clock]
            flag1_args, flag2_args, flag3_args, flag_vars_for_instance1, flag_args_for_instance2, flag_args_for_instance3 = flags.getArgs(*args_for_flags)
            
            elements1[elem1.getPK()] = (flags(*flag1_args), elem1)
            elements2[elem2.getPK()] = (flags(*flag2_args), elem2)
            elements3[elem3.getPK()] = (flags(*flag3_args), elem3)

            vars_for_instance1 += elem_vars_for_instance1 + flag_vars_for_instance1
            vars_for_instance2 += elem_args_for_instance2 + flag_args_for_instance2
            vars_for_instance3 += elem_args_for_instance3 + flag_args_for_instance3
        
        before_args1, before_args2, before_args3, before_args_for_instance1, before_args_for_instance2, before_args_for_instance3 = clock.getBeforeFunArgs("DWTab_"+extra_id)

        args1 = [elements1, *before_args1]
        args2 = [elements2, *before_args2]
        args3 = [elements3, *before_args3]

        vars_for_instance1 += before_args_for_instance1
        vars_for_instance2 += before_args_for_instance2
        vars_for_instance3 += before_args_for_instance3
        
        return args1, args2, args3, vars_for_instance1, vars_for_instance2, vars_for_instance3
