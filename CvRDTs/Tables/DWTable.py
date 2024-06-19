
from z3 import *
from typing import Callable, Dict, Tuple

from CvRDTs.Tables.PK import PK
from CvRDTs.Tables.Element import Element
from CvRDTs.Tables.DWFlags import DWFlags
from CvRDTs.Tables.Table import Table

from CvRDTs.Time.Time import Time
from CvRDTs.Tables.Flags_Constants import Status, Version
from PROOF_PARAMETERS import BEFORE_FUNCTION_TIME_TYPE, MAX_TABLES_SIZE_TO_PROVE 



class DWTable(Table):
    '''DWTable provides a default implementation of methods of the CvRDT.
       DWTable extends CvRDT. And CvRDT accepts a generic type T, which we here bind to DWTable.'''
    
    def __init__(self, elements: Dict[PK, Tuple[DWFlags, Element]], before: Callable[[Time, Time], bool]): 
        super().__init__(elements, before)

    def compatible(self, other: 'DWTable') -> BoolRef:
        '''for all elements in zip (this values(), that values()), check if they are compatible.
            (and to reduce search space for z3, we add some assumptions before)'''
        return And(
            self.before == other.before,
            # TODO: voltar a fazer os assumptions
            # self.beforeAssumptions(),
            # self.mergeValuesAssumptions(),
            # we use zip which iterate over the map without any order and without matching keys, but it's enough to check if the elements are compatible, they don't need to be the same one. And also if one table is bigger than the other, we don't need to check the rest of the elements.
            And(*[And(e1[0].compatible(e2[0]), e1[1].compatible(e2[1])) for (e1, e2) in zip(self.elements.values(), other.elements.values())])
        )
    
    def reachable(self) -> BoolRef : 
        '''for all elements in elements.values() check if they respect the conditions'''
        return And(*[And(   # check PK
                            pk.reachable(),
                            # check flags
                            elem[0].reachable(),
                            elem[0].flag != Status.DELETED,
                            len(elem[0].fk_versions) == self.getNumFKs(),
                            # check values
                            elem[1].reachable()
                        ) for pk, elem in self.elements.items()
                    ])

    
    def __eq__(self, other: 'DWTable') -> BoolRef:
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
    
    def equals(self, other: 'DWTable') -> BoolRef:
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
        

    def compare(self, other: 'DWTable') -> BoolRef:
        ''' Returns True if `self`<=`that`.
            for all elements in zip (this values(), that values()), check if they are comparable'''
        # TODO: mesmo que equals
        return And(*[And(e1[0].compare(e2[0]), e1[1].compare(e2[1])) for (e1, e2) in zip(self.elements.values(), other.elements.values())])

    def merge(self, other: 'DWTable'):
        '''for each PK in maps, choose the element with bigger version, else merge them, or if that PK is present only in one map, so keep it.'''
        # we can't use a simple zip because we need to merge elements with the same PK, and not the same index in the list. So we need to iterate over the keys of the maps: intersection_keys we know are in both maps, and the rest of the keys are in only one map.
        merged_elems = {}
        intersection_keys = set(self.elements.keys()).intersection(other.elements.keys())
        for pk in intersection_keys:
            e1 = self.elements.get(pk)
            e2 = other.elements.get(pk)
            merged_elem = e1[1].merge_with_version(e2[1], e1[0].version, e2[0].version)
            merged_flags = e1[0].merge(e2[0])
            merged_elems[pk] = (merged_flags, merged_elem)
        for pk in set(self.elements.keys()).union(other.elements.keys()).difference(intersection_keys):
            if pk in self.elements:
                merged_elems[pk] = self.elements[pk]
            else:
                merged_elems[pk] = other.elements[pk]       
        return self.copy(self.elements)


    # def beforeAssumptions(self):
    #     t1, t2, t3 = Ints('t1 t2 t3')
    #     return And(
    #         ForAll([t1], Not(self.before(t1, t1))),
    #         ForAll([t1, t2], Implies(self.before(t1, t2), Not(self.before(t2, t1)))),
    #         ForAll([t1, t2, t3], Implies(And(self.before(t1, t2), self.before(t2, t3)), self.before(t1, t3)))
    #     )

    
    # def mergeValuesAssumptions(self):
    #     v1, v2, v3 = V, V, V
    #     return And(
    #         ForAll([v1], v1.merge(v1) == v1),
    #         ForAll([v1, v2], v1.merge(v2) == v2.merge(v1)),
    #         ForAll([v1, v2, v3], v1.merge(v2).merge(v3) == v1.merge(v2.merge(v3)))
    #     )


    def getVersion(self, pk: PK) -> Int:
        if pk not in self.elements:
            return Version.ERROR_VERSION
        elem_flags = self.elements[pk][0]
        return If(is_true(elem_flags.flag == Status.VISIBLE), elem_flags.version, Version.ERROR_VERSION)   
    

    def setFlag(self, pk: PK, flag: Int):
        if pk not in self.elements:
            return self.copy(self.elements)
        elem = self.elements[pk]
        self.elements[pk] = (elem[0].set_flag(flag), elem[1])
        return self.copy(self.elements)


    @staticmethod
    def getArgs(extra_id: str, elem: Element):
        '''return symbolic all different variables for 3 different instances of a given concrete table, and also list of those variables to be used by Z3.'''

        vars_for_1_instance, vars_for_2_instances, vars_for_3_instances = [], [], []

        elements1, elements2, elements3 = {}, {}, {}
        for i in range(MAX_TABLES_SIZE_TO_PROVE):  
            elem1_args, elem2_args, elem3_args3, elem_vars_for_1_instance, elem_args_for_2_instances, elem_args_for_3_instances = elem.getArgs(str(i) + "_DWTab_" + extra_id)
            elem1, elem2, elem3 = elem(*elem1_args), elem(*elem2_args), elem(*elem3_args3)
            
            flag1_args, flag2_args, flag3_args, flag_vars_for_1_instance, flag_args_for_2_instances, flag_args_for_3_instances = DWFlags.getArgs(str(i) + "_DWTab_" + extra_id, elem.number_of_FKs)
            
            elements1[elem1.getPK()] = (DWFlags(*flag1_args), elem1)
            elements2[elem2.getPK()] = (DWFlags(*flag2_args), elem2)
            elements3[elem3.getPK()] = (DWFlags(*flag3_args), elem3)

            vars_for_1_instance += elem_vars_for_1_instance + flag_vars_for_1_instance
            vars_for_2_instances += elem_args_for_2_instances + flag_args_for_2_instances
            vars_for_3_instances += elem_args_for_3_instances + flag_args_for_3_instances
        

        before_args1, before_args2, before_args3, before_args_forAll_1, before_args_forAll_2, before_args_forAll_3 = BEFORE_FUNCTION_TIME_TYPE.getBeforeFunArgs(extra_id+"art_T")

        args1 = [elements1, *before_args1]
        args2 = [elements2, *before_args2]
        args3 = [elements3, *before_args3]

        vars_for_1_instance += before_args_forAll_1
        vars_for_2_instances += before_args_forAll_2
        vars_for_3_instances += before_args_forAll_3
        
        return args1, args2, args3, vars_for_1_instance, vars_for_2_instances, vars_for_3_instances

