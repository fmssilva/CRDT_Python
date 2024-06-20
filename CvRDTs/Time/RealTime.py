
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
        
        intTime1_args = [value1]
        intTime2_args = [value2]
        intTime3_args = [value3]

        vars_for_1_instance = [value1]
        vars_for_2_instances = [value1, value2]
        vars_for_3_instances = [value1, value2, value3]

        return intTime1_args, intTime2_args, intTime3_args, vars_for_1_instance, vars_for_2_instances, vars_for_3_instances
        
    
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
        var1, var2, var3, var4, var5, var6 = Ints(f'IntTime1_{extra_id} IntTime2_{extra_id} IntTime3_{extra_id} IntTime4_{extra_id} IntTime5_{extra_id} IntTime6_{extra_id}')
                                                  
        z3_vars_for_1_before_fun = [var1, var2]
        z3_vars_for_2_before_funs2 = [var1, var2, var3, var4]
        z3_vars_for_3_before_funs = [var1, var2, var3, var4, var5, var6]

        return before1_args, before2_args, before3_args, z3_vars_for_1_before_fun, z3_vars_for_2_before_funs2, z3_vars_for_3_before_funs
        