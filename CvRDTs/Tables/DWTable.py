
from z3 import *
from abc import abstractmethod
from typing import Callable, Dict, Generic, Tuple, TypeVar

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.Time import Time
from CvRDTs.Tables.DWFlags import DWFlags
from CvRDTs.Tables.Flags_Constants import Status, Version
from PROOF_PARAMETERS import BEFORE_FUNCTION_TIME_TYPE, MAX_TABLES_SIZE_TO_PROVE


PK = TypeVar('PK')  # PK is a generic type repreenting the Primary Key of the table, and of the Values themselves
V = TypeVar('V', bound='CvRDT')  # V is a generic type of the elements of the table, and they are bound to CvRDT


class DWTable(CvRDT['DWTable[PK,V]'], Generic[PK, V]):
    '''DWTable provides a default implementation of methods of the CvRDT.
       DWTable extends CvRDT. And CvRDT accepts a generic type T, which we here bind to DWTable[PK,V].'''
    
    def __init__(self, elements: Dict[PK, Tuple[DWFlags, V]], before: Callable[[Time, Time], bool]): 
        self.elements = elements  # elements is a dict with PK as key and (DWFlags, V) as value
        self.before = before  # before is a function (Time, Time) => Bool

    @abstractmethod
    def copy(self, newElements: Dict[PK, Tuple[DWFlags, V]]) -> 'DWTable':
        pass

    @abstractmethod
    def getNumFKs(self) -> int:
        pass
    

    def reachable(self) -> BoolRef : 
        '''for all elements in elements.values() check if they respect the conditions'''
        return And(*[
            And(
                # check flags
                elem[0].reachable(),
                elem[0].flag != Status.DELETED,
                len(elem[0].fk_versions) == self.getNumFKs(),
                # check values
                elem[1].reachable()
            ) for elem in self.elements.values()
        ])


    def equals(self, other: 'DWTable') -> BoolRef:
        '''for all elements in zip (this values(), that values()), check if they are equal'''
        return And(
            self.before == other.before,
            And(*[
                And(
                    e1[0].equals(e2[0]),
                    e1[1].equals(e2[1])
                ) for (e1, e2) in zip(self.elements.values(), other.elements.values())
            ])
        )

    def compare(self, other: 'DWTable') -> BoolRef:
        '''for all elements in zip (this values(), that values()), check if they are comparable'''
        return And(*[And(e1[0].compare(e2[0]), e1[1].compare(e2[1])) for (e1, e2) in zip(self.elements.values(), other.elements.values())])

    def compatible(self, other: 'DWTable') -> BoolRef:
        '''for all elements in zip (this values(), that values()), check if they are compatible.
            (and to reduce search space for z3, we add some assumptions before)'''
        return And(
            self.before == other.before,
            # TODO: voltar a fazer os assumptions
            # self.beforeAssumptions(),
            # self.mergeValuesAssumptions(),
            And(*[And(e1[0].compatible(e2[0]), e1[1].compatible(e2[1])) for (e1, e2) in zip(self.elements.values(), other.elements.values())])
        )

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

    def merge(self, other: 'DWTable'):
        '''for each PK in maps, choose the element with bigger version, else merge them, or if that PK is present only in one map, so keep it.'''
        merged_elems = {}
        for pk in set(self.elements.keys()).union(other.elements.keys()):
            e1 = self.elements.get(pk)
            e2 = other.elements.get(pk)
            if e1 and e2: # if both elements exist, keep the one with the highest version, or merge them
                if is_true(e1[0].version > e2[0].version):
                    merged_elems[pk] = e1
                elif is_true(e2[0].version > e1[0].version):
                    merged_elems[pk] = e2
                else:
                    merged_elems[pk] = (e1[0].merge(e2[0]), e1[1].merge(e2[1]))
            elif e1: # e2 is None
                merged_elems[pk] = e1
            elif e2: # e1 is None
                merged_elems[pk] = e2
        self.setFlag(pk, Status.VISIBLE)
        return self.copy(merged_elems)


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
    def getArgs(extra_id: str, v: V):
        '''return symbolic all different variables for 3 different instances of a given concrete table, and also list of those variables to be used by Z3.'''

        vars_for_1_instance, vars_for_2_instances, vars_for_3_instances = [], [], []

        elements1, elements2, elements3 = {}, {}, {}
        for i in range(MAX_TABLES_SIZE_TO_PROVE):  
            v1_args, v2_args, v3_args3, v_vars_for_1_instance, v_args_for_2_instances, v_args_for_3_instances = v.getArgs(extra_id+str(i))
            v1, v2, v3 = v(*v1_args), v(*v2_args), v(*v3_args3)
            
            flag1_args, flag2_args, flag3_args, flag_vars_for_1_instance, flag_args_for_2_instances, flag_args_for_3_instances = DWFlags.getArgs(extra_id+str(i), v.number_of_FKs)
            
            elements1[v1.getPK()] = (DWFlags(*flag1_args), v1)
            elements2[v2.getPK()] = (DWFlags(*flag2_args), v2)
            elements3[v3.getPK()] = (DWFlags(*flag3_args), v3)

            vars_for_1_instance += v_vars_for_1_instance + flag_vars_for_1_instance
            vars_for_2_instances += v_args_for_2_instances + flag_args_for_2_instances
            vars_for_3_instances += v_args_for_3_instances + flag_args_for_3_instances
        

        before_args1, before_args2, before_args3, before_args_forAll_1, before_args_forAll_2, before_args_forAll_3 = BEFORE_FUNCTION_TIME_TYPE.getBeforeFunArgs(extra_id+"art_T")

        args1 = [elements1, *before_args1]
        args2 = [elements2, *before_args2]
        args3 = [elements3, *before_args3]

        vars_for_1_instance += before_args_forAll_1
        vars_for_2_instances += before_args_forAll_2
        vars_for_3_instances += before_args_forAll_3
        
        return args1, args2, args3, vars_for_1_instance, vars_for_2_instances, vars_for_3_instances

