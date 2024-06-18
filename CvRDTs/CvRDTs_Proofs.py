
from typing import List
from z3 import *

from CvRDTs.CvRDT import T, CvRDT


class CvRDT_Proofs:
    '''CvRDTProofs provides the proofs that all CvRDTs must satisfy.'''
    
    def compare_correct(self, vars_for_2_instances: List[str], x: CvRDT[T], y: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_2_instances, Implies(
            And(x.reachable(), y.reachable(), x.compatible(y)),
            x.equals(y) == (x == y)
        ))

    def is_a_CvRDT(self, vars_for_3_instances: List[str], x: CvRDT[T], y: CvRDT[T], z: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_3_instances,Implies(
            And(
                x.reachable(), y.reachable(), z.reachable(),
                x.compatible(y), x.compatible(z), y.compatible(z)
            ),
            And(
                x.merge(x).equals(x),  # idempotent
                x.merge(y).equals(y.merge(x)),  # commutative
                x.merge(y).merge(z).equals(x.merge(y.merge(z))),  # associative
                x.merge(y).reachable(),  # merged state is reachable
                x.merge(y).merge(z).reachable(),
                x.compatible(y) == y.compatible(x)  # compatible commutes
            )
        ))

    ##################################################################
    # If the "is_a_CvRDT" proof is too big, and aborts without a result
    # so we can divide that proof in parts and run each part at a time
    ##################################################################

    def compatible_commutes(self, vars_for_2_instances: List[str], x: CvRDT[T], y: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_2_instances, Implies(
            And(x.reachable(), y.reachable()),
            x.compatible(y) == y.compatible(x)
        ))

    def merge_idempotent(self, vars_for_1_instances: List[str], x: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_1_instances, Implies(
            x.reachable(),
            x.merge(x).equals(x)
        ))

    def merge_commutative(self, vars_for_2_instances: List[str], x: CvRDT[T], y: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_2_instances, Implies(
            And(x.reachable(), y.reachable(), x.compatible(y)),
            And(
                x.merge(y).equals(y.merge(x)),
                x.merge(y).reachable()
            )
        ))

    def merge_associative(self, vars_for_3_instances: List[str], x: CvRDT[T], y: CvRDT[T], z: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_3_instances, Implies(
            And(
                x.reachable(), y.reachable(), z.reachable(),
                x.compatible(y), x.compatible(z), y.compatible(z)
            ),
            And(
                x.merge(y).merge(z).equals(x.merge(y.merge(z))),
                x.merge(y).merge(z).reachable()
            )
        ))

    def merge_reachable(self, vars_for_3_instances: List[str], x: CvRDT[T], y: CvRDT[T], z: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_3_instances, Implies(
            And(
                x.reachable(), y.reachable(), z.reachable(),
                x.compatible(y), x.compatible(z), y.compatible(z)
            ),
            And(
                x.merge(y).reachable(),
                x.merge(y).merge(z).reachable()
            )
        ))

    def merge_compatible(self, vars_for_3_instances: List[str], x: CvRDT[T], y: CvRDT[T], z: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_3_instances, Implies(
            And(
                x.reachable(), y.reachable(), z.reachable(),
                x.compatible(y), x.compatible(z), y.compatible(z)
            ),
            And(
                x.merge(y).compatible(z),
                x.compatible(y.merge(z))
            )
        ))

