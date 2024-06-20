
from z3 import *

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.Time import Time


class RealTime(Time, CvRDT['RealTime']):
    '''A class to represent a time as an integer value. extends Time abstract class.'''

    def __init__(self, value: Int):
        self.value = value

    ########################################################################
    ###################         CvRDT methods         ######################

    # compatible is True (they just need to be a number); so implemented in CvRDT class

    def reachable(self):
        return self.value >= 0 # it could be any number, but it's more logical and easier to understand that it starts in 0
    
    def __eq__(self, other: 'RealTime') -> bool:
        return self.value == other.value
    
    def equals(self, other: 'RealTime') -> BoolRef:
        '''we can override CvRDT equals, so we check == directly, instead of this <= that && that <= this''' 
        return self.value == other.value
    
    def compare(self, other: 'RealTime') -> BoolRef:
        '''This is not used if we override equals method from CvRDT class'''
        return self.beforeOrEqual(other)
    
    def merge(self, other: 'RealTime') -> 'RealTime':
        return RealTime(If (self.value >= other.value, self.value, other.value)) # LUB


    ########################################################################
    ###################         Time methods         ######################

    def before(self, other: 'RealTime') -> bool:
        return self.value < other.value

    def beforeOrEqual(self, other: 'RealTime') -> bool:
        return self.value <= other.value
    
    @staticmethod
    def getArgs(extra_id: str):
        '''return 3 instances of IntTime, and the needed symbolic varibales for all 3 instances.'''
        
        # Symbolic variables
        value1, value2, value3 = Ints(f'IntTime1_{extra_id} IntTime2_{extra_id} IntTime3_{extra_id}')
        
        time1_args = [value1]
        time2_args = [value2]
        time3_args = [value3]

        vars_for_instance1 = [value1]
        vars_for_instance2 = [value2]
        vars_for_instance3 = [value3]

        return time1_args, time2_args, time3_args, vars_for_instance1, vars_for_instance2, vars_for_instance3
    

    @staticmethod
    def getBeforeFunArgs(extra_id: str):
        '''return 3 symbolic functions of before: (Int, Int) -> Bool; and also the needed symbolic varibales for all 3 functions.'''
        
        # 3 symbolic "before" functions
        arg_type = IntSort() # function args type
        return_type = BoolSort() # function return type
        before1_args = [Function(f'before1_{extra_id}', arg_type, arg_type, return_type)] 
        before2_args = [Function(f'before2_{extra_id}', arg_type, arg_type, return_type)] 
        before3_args = [Function(f'before3_{extra_id}', arg_type, arg_type, return_type)] 

        # Symbolic variables for the args of the functions
        bef1_var1, bef1_var2, bef2_var1, bef2_var2, bef3_var1, bef3_var2 = Ints(f'RealTime1_before1_{extra_id} RealTime2_before1_{extra_id} RealTime1_before2_{extra_id} RealTime2_before2_{extra_id} RealTime1_before3_{extra_id} RealTime2_before3_{extra_id}')
                                                  
        z3_vars_for_before1 = [bef1_var1, bef1_var2]
        z3_vars_for_before2 = [bef2_var1, bef2_var2]
        z3_vars_for_before3 = [bef3_var1, bef3_var2]

        return before1_args, before2_args, before3_args, z3_vars_for_before1, z3_vars_for_before2, z3_vars_for_before3