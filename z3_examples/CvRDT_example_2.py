

''' 
Simple Example of how to use Z3 to prove properties.

Just do:    pip install z3-solver

And run this script.

In this example we have 2 implementations of merge. 
Set MERGE_COMUTATIVE_SOULD_HOLD to True or False, and so the solver will run with different implementations of merge.
    - the mergeCommutative proof  will hold or not hold according to our selection
    - the mergeIdempotent proof will always hold 

'''

MERGE_COMUTATIVE_SOULD_HOLD = False

################### SIMPLE EXAMPLE ###################
'''Some details to have in mind when programming with Z3:
    Data types: Z3 has its own data types, so Int, BoolRef, etc and not python data types (int, bool, etc)
    Funcions/Operators: Z3 has its own functions, so use Implies, And, Or, etc and not python functions (and, or, ==, etc)
    import: for all this to work, you need to import Z3: from z3 import *
    '''



from abc import ABC, abstractmethod   # Abstract Base Class to force child classes to implement methods that have the @abstractmethod decorator
from typing import List, TypeVar, Generic
from z3 import *

T = TypeVar('T', bound='CvRDT')


# CvRDT defines the methods that all CvRDTs must implement
class CvRDT(ABC, Generic[T]):
    @abstractmethod
    def merge(self, that: T) -> T:
        pass
    @abstractmethod
    def equals(self, that: T) -> BoolRef:
        pass
    @abstractmethod
    def reachable(self) -> BoolRef:
        pass


# Concrete CvRDTs make their own implementation of CvRDT methods, and other methods as needed
class ConcreteCvRDT(CvRDT['ConcreteCvRDT']):
    
    def __init__(self, value: Int, vList: List[Int]): # Use Z3 types (Int and not int) (and so have "from z3 import *" to be recognized)
        super().__init__()
        self.value = value
        self.vList = vList

    def merge(self, that: 'ConcreteCvRDT') -> 'ConcreteCvRDT':
        if MERGE_COMUTATIVE_SOULD_HOLD:
            mergedList = [v1 + v2 for v1, v2 in zip(self.vList, that.vList)]
            return ConcreteCvRDT(self.value + that.value, mergedList)
        return ConcreteCvRDT(self.value, self.vList)
    
    def equals(self, that: 'ConcreteCvRDT') -> BoolRef:
        return And (
            self.value == that.value, 
            And([v1 == v2 for v1, v2 in zip(self.vList, that.vList)])
        )
    
    def reachable(self) -> BoolRef:
        return And (
            self.value >= 0, 
            And([v >= 0 for v in self.vList])
        )
    
    @staticmethod
    def getArgs():
        ''' - we can ask each class to give us the variables that we'll use to instanciate it, 
                so we can create a main() method more flexible and easy to use with diferent classes.
            - python uses "normal" variables, but Z3 uses its own, so we need to bind the python variables to Z3 variables.
            - Z3 WILL GIVE THE SAME VALUES TO VARIABLES WITH THE SAME NAME
                so make sure to use different names, example:
                    - for multiple instances of the same class, different variable names for each to have different values 
                    - for a list, give a different name to the variable of each position, example appending 'idx' to the name
                    - for a class that receives another class as argument, also give different names, example in complex systems, maybe append the name of the class to each variable so the variable "name" in both classes get different names 
            - When some class receives another class as argument, we need to instanciate that class before passing it to the solver'''

        value1 = Int('value1')
        value2 = Int('value2')
        vList1 = [Int(f'vList1_{i}') for i in range(3)]
        vList2 = [Int(f'vList2_{i}') for i in range(3)]

        args1 = value1, vList1 # args to instanciate the class
        args2 = value2, vList2
        args_forAll_1 = [value1] + vList1 # args to use in ForAll with 1 instance of the class
        args_forAll_2 = [value1, value2] + vList1 + vList2 # args to use in ForAll with 2 instances of the class

        return args1, args2, args_forAll_1, args_forAll_2


class ConcreteCvRDT_2(CvRDT['ConcreteCvRDT_2']):
    def __init__(self, value: Int, cvdrt: ConcreteCvRDT):
        super().__init__()
        self.value = value
        self.cvdrt = cvdrt
    
    def merge(self, that: 'ConcreteCvRDT_2') -> 'ConcreteCvRDT_2':
        return ConcreteCvRDT_2(self.value + that.value, self.cvdrt.merge(that.cvdrt))
    
    def equals(self, that: 'ConcreteCvRDT_2') -> BoolRef:
        return And (
            self.value == that.value, 
            self.cvdrt.equals(that.cvdrt)
        )
    
    def reachable(self) -> BoolRef:
        return And (
            self.value >= 0, 
            self.cvdrt.reachable()
        )

    @staticmethod
    def getArgs():
        value1 = Int('value1')
        value2 = Int('value2')
        c_args1, c_args2, c_args_forAll_1, c_args_forAll_2 = ConcreteCvRDT.getArgs()
        
        args1 = value1, ConcreteCvRDT(*c_args1)
        args2 = value2, ConcreteCvRDT(*c_args2)
        args_forAll_1 = [value1] + c_args_forAll_1
        args_forAll_2 = [value1, value2] + c_args_forAll_1 + c_args_forAll_2

        return args1, args2, args_forAll_1, args_forAll_2




# CvRDTProof defines the properties that all CvRDTs must satisfy
class CvRDTProofs:
    def __init__(self):
        pass
    
    def merge_idempotent(self, this: CvRDT[T]) -> BoolRef: # For proofs, we use Z3 types (BoolRef and not Bool or bool)
        return Implies(
            this.reachable(),
            this.merge(this).equals(this)
        )

    def merge_commutative(self, this: CvRDT[T], that: CvRDT[T]) -> BoolRef:
        return Implies(
            And (this.reachable(), that.reachable()),
            this.merge(that).equals(that.merge(this))
        )


####################      RUN         ####################

CvRDT_TO_PROVE = 1
CvRDT_OPTIONS = { 1: ConcreteCvRDT, 2: ConcreteCvRDT_2}


# Example of how to use the proofs
if __name__ == "__main__":
    
    print("\nRun proofs...")

    solver = Solver()
    proofs = CvRDTProofs()
    CvRDT_to_prove = CvRDT_OPTIONS[CvRDT_TO_PROVE]

    args1, args2, args_forAll_1, args_forAll_2 = CvRDT_to_prove.getArgs()

    # RUN PROOFS
    solver.add(ForAll(args_forAll_1, proofs.merge_idempotent(CvRDT_to_prove(*args1))))
    result = solver.check()
    print("mergeIdempotent - holds ?  ", (result == sat))
    print("model:   ", solver.model() if result == sat else solver.unsat_core())

    solver.reset()  # remove solver constrains before adding new ones
    
    solver.add(ForAll(args_forAll_2, proofs.merge_commutative(CvRDT_to_prove(*args1), CvRDT_to_prove(*args2))))
    result = solver.check()
    print("mergeCommutative - holds ?  ", (result == sat))
    print("model:   ", solver.model() if result == sat else solver.unsat_core())
    
    if not MERGE_COMUTATIVE_SOULD_HOLD:
        print("Finding a counter example for mergeCommutative")
        solver.reset()  
        solver.add(Exists(args_forAll_2, Not(proofs.merge_commutative(CvRDT_to_prove(*args1), CvRDT_to_prove(*args2)))))
        result = solver.check()
        print("mergeCommutative - holds ?  ", (result == sat))
        # value1 = Int('value1')
        # value2 = Int('value2')
        # vList1 = [Int(f'vList1_{i}') for i in range(3)]
        # vList2 = [Int(f'vList2_{i}') for i in range(3)]
        m = solver.model()
        print("model:   ", m)
        print("value1: ", m[args1[0]])



