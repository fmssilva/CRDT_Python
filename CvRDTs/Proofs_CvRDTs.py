
from z3 import *
from typing import List

from CvRDTs.CvRDT import T, CvRDT



class Proofs_CvRDT:
    '''CvRDTProofs provides the proofs that all CvRDTs must satisfy.'''

    @staticmethod
    def compare_correct(vars_for_2_instances: List[str], x: CvRDT[T], y: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_2_instances, 
            Implies(
                And(x.compatible(y), x.reachable(), y.reachable()),
                x.equals(y) == (x == y)
            ))  

    @staticmethod
    def is_a_CvRDT(vars_for_3_instances: List[str], x: CvRDT[T], y: CvRDT[T], z: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_3_instances,
            Implies(
                And(x.compatible(y), x.compatible(z), y.compatible(z),
                    x.reachable(), y.reachable(), z.reachable()),
                And(x.merge(x).equals(x),  # idempotent
                    x.merge(y).equals(y.merge(x)),  # commutative
                    x.merge(y).merge(z).equals(x.merge(y.merge(z))),  # associative
                    x.merge(y).reachable(),  # merged state is reachable
                    x.merge(y).merge(z).reachable(),
                    x.compatible(y) == y.compatible(x))  # compatible commutes
            ))

    ##################################################################
    # If the "is_a_CvRDT" proof is too big, and aborts without a result
    # so we can divide that proof in parts and run each part at a time
    ##################################################################

    @staticmethod
    def compatible_commutes(vars_for_2_instances: List[str], x: CvRDT[T], y: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_2_instances, 
            Implies(
                And(x.compatible(y), x.reachable(), y.reachable()),
                x.compatible(y) == y.compatible(x)
            ))
       

    @staticmethod
    def merge_idempotent(vars_for_1_instances: List[str], x: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_1_instances, 
            Implies(
                x.reachable(),
                x.merge(x).equals(x)
            ))
       

    @staticmethod
    def merge_commutative(vars_for_2_instances: List[str], x: CvRDT[T], y: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_2_instances, 
            Implies(
                And(x.compatible(y), x.reachable(), y.reachable()),
                x.merge(y).equals(y.merge(x))
            ))
       

    @staticmethod
    def merge_associative(vars_for_3_instances: List[str], x: CvRDT[T], y: CvRDT[T], z: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_3_instances, 
            Implies(
                And(x.compatible(y), x.compatible(z), y.compatible(z),
                    x.reachable(), y.reachable(), z.reachable()), 
                x.merge(y).merge(z).equals(x.merge(y.merge(z)))
            ))
      

    @staticmethod
    def merge_reachable(vars_for_3_instances: List[str], x: CvRDT[T], y: CvRDT[T], z: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_3_instances, 
            Implies(
                And(x.compatible(y), x.compatible(z), y.compatible(z),
                    x.reachable(), y.reachable(), z.reachable()), 
                And(x.merge(y).reachable(),
                    x.merge(y).merge(z).reachable())
            ))
      

    @staticmethod
    def merge_compatible(vars_for_3_instances: List[str], x: CvRDT[T], y: CvRDT[T], z: CvRDT[T]) -> BoolRef:
        return ForAll(vars_for_3_instances, 
            Implies(
                And(x.compatible(y), x.compatible(z), y.compatible(z),
                    x.reachable(), y.reachable(), z.reachable()), 
                And(x.merge(y).compatible(z),
                    x.compatible(y.merge(z)))
            ))
       