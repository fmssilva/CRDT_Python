

from z3 import *
from typing import List



''' Simple class to show a proof of a class with other objects as arguments.
    For example the OuterClass has 2 BiggerValues as arguments.
    
    Important to see that the OuterClass methods just call the BiggerValue methods.

    Important to see the attention we need to have to give different names to the symbolic variables of the objects.
    example now that we have 2 objects of the same type, and each of them with 3 instances, we need to give different names to all of that: 
            bv1_instance1_args = [Int(f'bv1_inst1_{i}') for i in range(10)]
            bv1_instance2_args = [Int(f'bv1_inst2_{i}') for i in range(10)]
            bv1_instance3_args = [Int(f'bv1_inst3_{i}') for i in range(10)]

            bv2_instance1_args = [Int(f'bv2_inst1_{i}') for i in range(10)]
            bv2_instance2_args = [Int(f'bv2_inst2_{i}') for i in range(10)]
            bv2_instance3_args = [Int(f'bv2_inst3_{i}') for i in range(10)]
    '''




##################################################################
##################       BiggerValue      ##############################

class BiggerValue:
    
    def __init__(self, values: List[int]):
        self.values = values
    
    def __eq__ (self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(*[self.values[i] == that.values[i] for i in range(len(self.values))])
    

    def equals(self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(self.compare(that), that.compare(self))
    
    def compare(self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(*[self.values[i] <= that.values[i] for i in range(len(self.values))])
    
    def compatible(self, that: 'BiggerValue') -> BoolRef:
        return len(self.values) == len(that.values)
        
    def reachable(self) -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(*[self.values[i] >= 0 for i in range(len(self.values))])
        
    def merge(self, that: 'BiggerValue') -> 'BiggerValue':
        '''@Pre: self.compatible(that)'''
        return BiggerValue([If(self.values[i] > that.values[i], self.values[i], that.values[i]) for i in range(len(self.values))])
    


class OuterClass:
    
    def __init__(self, bv1: BiggerValue, bv2: BiggerValue):
        self.bv1 = bv1
        self.bv2 = bv2
    
    def __eq__ (self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(self.bv1.__eq__(that.bv1), self.bv2.__eq__(that.bv2))
    
    def equals(self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(self.compare(that), that.compare(self))
    
    def compare(self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(self.bv1.compare(that.bv1), self.bv2.compare(that.bv2))
            
    def compatible(self, that: 'BiggerValue') -> BoolRef:
        return And(self.bv1.compatible(that.bv1), self.bv2.compatible(that.bv2))
        
    def reachable(self) -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(self.bv1.reachable(), self.bv2.reachable())
        
    def merge(self, that: 'BiggerValue') -> 'BiggerValue':
        '''@Pre: self.compatible(that)'''
        return OuterClass(self.bv1.merge(that.bv1), self.bv2.merge(that.bv2))


##################################################################
##################       PROOFS      #############################

class Proofs:
    '''A class to define the properties that all BiggerValues must satisfy'''
    
    @staticmethod
    def compare_correct(vars_for_2_instances: List[str], x: BiggerValue, y: BiggerValue) -> BoolRef:
        return ForAll(vars_for_2_instances, 
            Implies(
                And(x.compatible(y), x.reachable(), y.reachable()),
                x.equals(y) == (x == y)
            ))    
       
    @staticmethod
    def compatible_commutes(vars_for_2_instances: List[str], x: BiggerValue, y: BiggerValue) -> BoolRef:
        return ForAll(vars_for_2_instances, 
            Implies(
                And(x.compatible(y), x.reachable(), y.reachable()),
                x.compatible(y) == y.compatible(x)
            ))
       

    @staticmethod
    def merge_idempotent(vars_for_1_instances: List[str], x: BiggerValue) -> BoolRef:
        return ForAll(vars_for_1_instances, 
            Implies(
                x.reachable(),
                x.merge(x).equals(x)
            ))
       

    @staticmethod
    def merge_commutative(vars_for_2_instances: List[str], x: BiggerValue, y: BiggerValue) -> BoolRef:
        return ForAll(vars_for_2_instances, 
            Implies(
                And(x.compatible(y), x.reachable(), y.reachable()),
                x.merge(y).equals(y.merge(x))
            ))
       

    @staticmethod
    def merge_associative(vars_for_3_instances: List[str], x: BiggerValue, y: BiggerValue, z: BiggerValue) -> BoolRef:
        return ForAll(vars_for_3_instances, 
            Implies(
                And(x.compatible(y), x.compatible(z), y.compatible(z),
                    x.reachable(), y.reachable(), z.reachable()), 
                x.merge(y).merge(z).equals(x.merge(y.merge(z)))
            ))
      

    @staticmethod
    def merge_reachable(vars_for_3_instances: List[str], x: BiggerValue, y: BiggerValue, z: BiggerValue) -> BoolRef:
        return ForAll(vars_for_3_instances, 
            Implies(
                And(x.compatible(y), x.compatible(z), y.compatible(z),
                    x.reachable(), y.reachable(), z.reachable()), 
                And(x.merge(y).reachable(),
                    x.merge(y).merge(z).reachable())
            ))
      

    @staticmethod
    def merge_compatible(vars_for_3_instances: List[str], x: BiggerValue, y: BiggerValue, z: BiggerValue) -> BoolRef:
        return ForAll(vars_for_3_instances, 
            Implies(
                And(x.compatible(y), x.compatible(z), y.compatible(z),
                    x.reachable(), y.reachable(), z.reachable()), 
                And(x.merge(y).compatible(z),
                    x.compatible(y.merge(z)))
            ))
       


###################################################################
##################       HELPER FUNCTION      #####################

def print_proof(proof_name: str, solver: Solver):
    print(f"Proof  {proof_name}  -  holds?     ", end=" ")
    if solver.check() == sat:
        print("sat")
        print(solver.model())
    else:
        print("unsat")
        print(solver.unsat_core())
    solver.reset() # Reset solver to clean the previous constraints



if __name__ == "__main__":
    
    # Define symbolic variables (all different names for Z3 proofs)
    bv1_instance1_args = [Int(f'bv1_inst1_{i}') for i in range(10)]
    bv1_instance2_args = [Int(f'bv1_inst2_{i}') for i in range(10)]
    bv1_instance3_args = [Int(f'bv1_inst3_{i}') for i in range(10)]

    bv2_instance1_args = [Int(f'bv2_inst1_{i}') for i in range(10)]
    bv2_instance2_args = [Int(f'bv2_inst2_{i}') for i in range(10)]
    bv2_instance3_args = [Int(f'bv2_inst3_{i}') for i in range(10)]

    # Create instances
    bv1_inst1 = BiggerValue(bv1_instance1_args)
    bv1_inst2 = BiggerValue(bv1_instance2_args)
    bv1_inst3 = BiggerValue(bv1_instance3_args)

    bv2_inst1 = BiggerValue(bv2_instance1_args)
    bv2_inst2 = BiggerValue(bv2_instance2_args)
    bv2_inst3 = BiggerValue(bv2_instance3_args)

    # Create instances of the OuterClass
    b1 = OuterClass(bv1_inst1, bv2_inst1)
    b2 = OuterClass(bv1_inst2, bv2_inst2)
    b3 = OuterClass(bv1_inst3, bv2_inst3)

    # Create Lists of symbolic variables for the proofs
    vars_for_1_instance = bv1_instance1_args + bv2_instance1_args
    vars_for_2_instances = vars_for_1_instance + bv1_instance2_args + bv2_instance2_args
    vars_for_3_instances = vars_for_2_instances + bv1_instance3_args + bv2_instance3_args
    
    solver = Solver()

    proofs = Proofs()
    
    # Proofs
    solver.add(proofs.compare_correct(vars_for_2_instances, b1, b2))
    print_proof("compare_correct", solver)
    
    solver.add(proofs.compatible_commutes(vars_for_2_instances, b1, b2))
    print_proof("compatible_commutes", solver)
    
    solver.add(proofs.merge_idempotent(vars_for_1_instance, b1))
    print_proof("merge_idempotent", solver)
    
    solver.add(proofs.merge_commutative(vars_for_2_instances, b1, b2))
    print_proof("merge_commutative", solver)
    
    solver.add(proofs.merge_associative(vars_for_3_instances, b1, b2, b3))
    print_proof("merge_associative", solver)
    
    solver.add(proofs.merge_reachable(vars_for_3_instances, b1, b2, b3))
    print_proof("merge_reachable", solver)
    
    solver.add(proofs.merge_compatible(vars_for_3_instances, b1, b2, b3))
    print_proof("merge_compatible", solver)
