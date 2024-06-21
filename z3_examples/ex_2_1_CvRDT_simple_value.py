from typing import List
from z3 import *



''' Simple BiggerValue proof example. 
    Important to see how to define proofs for BiggerValues using Z3...
    
    And important to confirm that python treats (==) as checking equal objects references in memory, 
    So we need to implement __eq__ in our classes to compare values, because if not the objects will always be different.'''




##################################################################
##################       BiggerValue      ##############################
  
class BiggerValue:
    '''A simple class to represent BiggerValue, basically a value that is bigger than or equal to 0.'''
    def __init__(self, value: Int):
        self.value = value
    
    #     
    # 
    #   Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.
    # 
    # 

    def __eq__ (self, that: 'BiggerValue') -> BoolRef:
        return self.value == that.value
    
    def equals(self, that: 'BiggerValue') -> BoolRef:
        return And(self.compare(that), that.compare(self))
    
    def compare(self, that: 'BiggerValue') -> BoolRef:
        return self.value <= that.value
    
    def compatible(self, that: 'BiggerValue') -> BoolRef:
        return True
    
    def reachable(self) -> BoolRef:
        return self.value >= 0
        
    def merge(self, that: 'BiggerValue') -> 'BiggerValue':
        return BiggerValue(If(self.value >= that.value, self.value, that.value))
    

##################################################################
##################       PROOFS      #############################

class Proofs:
    '''A class to define the properties that all BiggerValues must satisfy'''
    
    @staticmethod
    def compare_correct(vars_for_2_instances: List[str], x: BiggerValue, y: BiggerValue) -> BoolRef:
        return ForAll(vars_for_2_instances, 
            Implies(
                And(x.reachable(), y.reachable(), x.compatible(y)),
                x.equals(y) == (x == y)
            ))    
       
    @staticmethod
    def compatible_commutes(vars_for_2_instances: List[str], x: BiggerValue, y: BiggerValue) -> BoolRef:
        return ForAll(vars_for_2_instances, 
            Implies(
                And(x.reachable(), y.reachable(), x.compatible(y)),
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
                And(x.reachable(), y.reachable(), x.compatible(y)),
                x.merge(y).equals(y.merge(x))
            ))
       

    @staticmethod
    def merge_associative(vars_for_3_instances: List[str], x: BiggerValue, y: BiggerValue, z: BiggerValue) -> BoolRef:
        return ForAll(vars_for_3_instances, 
            Implies(
                And(x.reachable(), y.reachable(), z.reachable(),
                    x.compatible(y), x.compatible(z), y.compatible(z)), 
                x.merge(y).merge(z).equals(x.merge(y.merge(z)))
            ))
      

    @staticmethod
    def merge_reachable(vars_for_3_instances: List[str], x: BiggerValue, y: BiggerValue, z: BiggerValue) -> BoolRef:
        return ForAll(vars_for_3_instances, 
            Implies(
                And(
                    x.reachable(), y.reachable(), z.reachable(),
                    x.compatible(y), x.compatible(z), y.compatible(z)),
                And(
                    x.merge(y).reachable(),
                    x.merge(y).merge(z).reachable())
            ))
      

    @staticmethod
    def merge_compatible(vars_for_3_instances: List[str], x: BiggerValue, y: BiggerValue, z: BiggerValue) -> BoolRef:
        return ForAll(vars_for_3_instances, 
            Implies(
                And(
                    x.reachable(), y.reachable(), z.reachable(),
                    x.compatible(y), x.compatible(z), y.compatible(z)),
                And(
                    x.merge(y).compatible(z),
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
    # Define symbolic variables
    x, y, z = Ints('x y z')

    # Create instances
    b1 = BiggerValue(x)
    b2 = BiggerValue(y)
    b3 = BiggerValue(z)

    # Create Lists of symbolic variables for the proofs
    vars_for_1_instance = [x]
    vars_for_2_instances = [x, y]
    vars_for_3_instances = [x, y, z]

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
