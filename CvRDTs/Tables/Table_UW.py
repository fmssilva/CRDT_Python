
from z3 import *
from typing import Callable, Dict, Tuple

from CvRDTs.Tables.PK import PK
from CvRDTs.Tables.Element import Element
from CvRDTs.Tables.Flags_UW import Flags_UW
from CvRDTs.Tables.Table import Table

from CvRDTs.Time.Time import Time
from CvRDTs.Tables.Flags import Status, Version



class Table_UW(Table):
    '''UWTable provides a default implementation of methods of the CvRDT.'''
    
    def __init__(self, elements: Dict[PK, Tuple[Flags_UW, Element]], before: Callable[[Time, Time], bool]): 
        super().__init__(elements, before)

    def reachable_complement(self, flags: 'Flags_UW') -> BoolRef:
        '''reachable method implemented in Table, and here the complement for the Update Wins Table.'''
        return True

    def merge(self, other: 'Table_UW'):
        '''for each PK in maps, choose the element with bigger version, else merge them, or if that PK is present only in one map, so keep it.'''
        # we can't use a simple zip because we need to merge elements with the same PK, and not the same index in the list. So we need to iterate over the keys of the maps: intersection_keys we know are in both maps, and the rest of the keys are in only one map.
        merged_elems = {}
        intersection_keys = set(self.elements.keys()).intersection(other.elements.keys())
        for pk in intersection_keys:
            e1 = self.elements.get(pk)
            e2 = other.elements.get(pk)
            # merged_elem = e1[1].merge_with_version(e2[1], e1[0].version, e2[0].version)
            merged_elem = e1[1].merge(e2[1])

            merged_flags = e1[0].merge(e2[0])
            merged_elems[pk] = (merged_flags, merged_elem)
        for pk in set(self.elements.keys()).union(other.elements.keys()).difference(intersection_keys):
            if pk in self.elements:
                merged_elems[pk] = self.elements[pk]
            else:
                merged_elems[pk] = other.elements[pk]       
        return self.copy(self.elements)


    def getVersion(self, pk: PK) -> Int:
        if pk not in self.elements:
            return Version.ERROR_VERSION
        elem_flags = self.elements[pk][0]
        return If(is_true(elem_flags.DI_flag == Status.VISIBLE), elem_flags.version, Version.ERROR_VERSION)   
    

    def setFlag(self, pk: PK, flag: Int):
        if pk not in self.elements:
            return self.copy(self.elements)
        elem = self.elements[pk]
        self.elements[pk] = (elem[0].set_flag(flag), elem[1])
        return self.copy(self.elements)


    ###############################################################
    #####################  Methods for Proofs  ####################

    @staticmethod
    def getArgs(extra_id: str, elem: Element, table_size: int, clock: Time ):
        '''return symbolic all different variables for 3 different instances of a given concrete table, and also list of those variables to be used by Z3.'''
        return Table.getArgs("DW_Table_"+extra_id, elem, table_size, clock, Flags_UW)
