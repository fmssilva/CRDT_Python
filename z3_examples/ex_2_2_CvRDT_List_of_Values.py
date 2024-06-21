from typing import List
from z3 import *



'''Simple class to show a proof of a class with some Data Structure.

    Also show that in our proofs, 
    we might want to order our conditions so the easier conditions are done first. 
    for example in this case our compatible is much more litter than reachable, 
    so we write:
            Implies(
                And(x.compatible(y), x.reachable(), y.reachable()),
                x.equals(y) == (x == y))
    
    TODO: confirm how Z3 works, if it organizes the constraints with some kind of optimization, maybe we don't need to worry about the order of the conditions.

'''



##################################################################
##################       BiggerValue      ##############################
  
class BiggerValue:
    
    def __init__(self, values: List[int]):
        self.values = values
    
    #     
    # 
    #   Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.
    # 
    # 

    def compatible(self, that: 'BiggerValue') -> BoolRef:
        return len(self.values) == len(that.values)

    def reachable(self) -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(*[self.values[i] >= 0 for i in range(len(self.values))])
   
    def __eq__ (self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(*[v1 == v2 for v1, v2 in zip(self.values, that.values)])
    

    def equals(self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(self.compare(that), that.compare(self))
    
    def compare(self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(*[self.values[i] <= that.values[i] for i in range(len(self.values))])
           
        
    def merge(self, that: 'BiggerValue') -> 'BiggerValue':
        '''@Pre: self.compatible(that)'''
        return BiggerValue([If(self.values[i] > that.values[i], self.values[i], that.values[i]) for i in range(len(self.values))])
    

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
    instance1_args = [Int(f'inst1_{i}') for i in range(10)]
    instance2_args = [Int(f'inst2_{i}') for i in range(10)]
    instance3_args = [Int(f'inst3_{i}') for i in range(10)]

    # Create instances
    b1 = BiggerValue(instance1_args)
    b2 = BiggerValue(instance2_args)
    b3 = BiggerValue(instance3_args)

    # Create Lists of symbolic variables for the proofs
    vars_for_1_instance = instance1_args
    vars_for_2_instances = instance1_args + instance2_args
    vars_for_3_instances = instance1_args + instance2_args + instance3_args
    
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
