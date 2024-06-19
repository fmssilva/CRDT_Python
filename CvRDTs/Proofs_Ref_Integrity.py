
from typing import List
from z3 import *

from CvRDTs.Tables.FK_System import FK_System
from CvRDTs.Tables.PK import PK


class Proofs_Ref_Integrity:
    '''Ref_Integrity_Proofs provides the proofs that a Table must satisfy to keep referential integrity.'''
    
    @staticmethod
    def generic_referential_integrity(vars_for_2_FK_Syst_inst_and_1_pk_inst: List[str], s1: 'FK_System', s2: 'FK_System', pk: PK) -> BoolRef:
        return ForAll(vars_for_2_FK_Syst_inst_and_1_pk_inst, Implies(
            And(
                s1.compatible(s2),
                s1.reachable(), s2.reachable(),
                s1.ref_integrity_holds_elem(pk), s2.ref_integrity_holds_elem(pk)
            ),
            s1.merge(s2).ref_integrity_holds_elem(pk)
        ))


