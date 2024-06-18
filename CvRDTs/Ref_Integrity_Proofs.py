
from typing import List
from z3 import *

from ConcreteTables.Alb import AlbPK
from ConcreteTables.Alb_FK_System import Alb_FK_System
from ConcreteTables.Art import ArtPK
from CvRDTs.CvRDT import T, CvRDT


class Ref_Integrity_Proofs:
    '''Ref_Integrity_Proofs provides the proofs that a Table must satisfy to keep referential integrity.'''
    
  
    def generic_referential_integrity(self, vars_for_2_FK_Syst_inst_and_1_pk_inst: List[str], s1: 'Alb_FK_System', s2: 'Alb_FK_System', pk: AlbPK) -> BoolRef:
        return ForAll(vars_for_2_FK_Syst_inst_and_1_pk_inst, Implies(
            And(
                s1.compatible(s2),
                s1.reachable(), s2.reachable(),
                s1.ref_integrity_holds_elem(pk), s2.ref_integrity_holds_elem(pk)
            ),
            s1.merge(s2).ref_integrity_holds_elem(pk)
        ))


