

from z3 import *
from typing import List

from CvRDTs.CvRDT import CvRDT



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

class BiggerValue(CvRDT['BiggerValue']):
    
    def __init__(self, values: List[int]):
        self.values = values
    
    def compatible(self, that: 'BiggerValue') -> BoolRef:
        return len(self.values) == len(that.values)

    def reachable(self) -> BoolRef:
        return And(*[value >= 0 for value in self.values])

    def __eq__ (self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(*[v1 == v2 for v1, v2 in zip(self.values, that.values)])
    

    # def equals(self, that: 'BiggerValue') -> BoolRef:
    #     '''@Pre: self.compatible(that)'''
    #     return And(self.compare(that), that.compare(self))
    
    def compare(self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(*[self.values[i] <= that.values[i] for i in range(len(self.values))])
            
        
    def merge(self, that: 'BiggerValue') -> 'BiggerValue':
        '''@Pre: self.compatible(that)'''
        return BiggerValue([If(self.values[i] > that.values[i], self.values[i], that.values[i]) for i in range(len(self.values))])
    


class TestClass(CvRDT['BiggerValue']):
    
    def __init__(self, bv1: BiggerValue, bv2: BiggerValue):
        self.bv1 = bv1
        self.bv2 = bv2
    
    def __eq__ (self, that: 'BiggerValue') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(self.bv1.__eq__(that.bv1), self.bv2.__eq__(that.bv2))
    
    # def equals(self, that: 'BiggerValue') -> BoolRef:
    #     '''@Pre: self.compatible(that)'''
    #     return And(self.compare(that), that.compare(self))
    
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
        return TestClass(self.bv1.merge(that.bv1), self.bv2.merge(that.bv2))

    @staticmethod
    def getArgs(extra_id:str):
        # Define symbolic variables (all different names for Z3 proofs)
        bv1_instance1_args = [Int(f'bv1_inst1_{i}_{extra_id}') for i in range(10)]
        bv1_instance2_args = [Int(f'bv1_inst2_{i}_{extra_id}') for i in range(10)]
        bv1_instance3_args = [Int(f'bv1_inst3_{i}_{extra_id}') for i in range(10)]

        bv2_instance1_args = [Int(f'bv2_inst1_{i}_{extra_id}') for i in range(10)]
        bv2_instance2_args = [Int(f'bv2_inst2_{i}_{extra_id}') for i in range(10)]
        bv2_instance3_args = [Int(f'bv2_inst3_{i}_{extra_id}') for i in range(10)]

        # Create instances
        bv1_inst1 = BiggerValue(bv1_instance1_args)
        bv1_inst2 = BiggerValue(bv1_instance2_args)
        bv1_inst3 = BiggerValue(bv1_instance3_args)

        bv2_inst1 = BiggerValue(bv2_instance1_args)
        bv2_inst2 = BiggerValue(bv2_instance2_args)
        bv2_inst3 = BiggerValue(bv2_instance3_args)

        # Args to create instances of the OuterClass
        outClass1_args = [bv1_inst1, bv2_inst1]
        outClass2_args = [bv1_inst2, bv2_inst2]
        outClass3_args = [bv1_inst3, bv2_inst3]

        # Create Lists of symbolic variables for the proofs
        vars_for_1_instance = bv1_instance1_args + bv2_instance1_args
        vars_for_2_instances = vars_for_1_instance + bv1_instance2_args + bv2_instance2_args
        vars_for_3_instances = vars_for_2_instances + bv1_instance3_args + bv2_instance3_args
        
        return outClass1_args, outClass2_args, outClass3_args, vars_for_1_instance, vars_for_2_instances, vars_for_3_instances

