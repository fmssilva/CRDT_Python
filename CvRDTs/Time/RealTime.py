
from z3 import *

from CvRDTs.Time.Time import Time


class RealTime(Time):
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
    
    def __hash__(self) -> int:
        '''because we implement __eq__, we must implement __hash__ to be able to use RealTime as a key in a dictionary.'''
        return hash(self.value)
    
    # equals defined in CvRDT
    
    def compare(self, other: 'RealTime') -> BoolRef:
        '''This is not used if we override equals method from CvRDT class'''
        return self.before_or_equal(other)
    
    def merge(self, other: 'RealTime') -> 'RealTime':
        return RealTime(If (self.before_or_equal(other), other.value, self.value)) # LUB


    ########################################################################
    ###################         Time methods         ######################

    def before(self, other: 'RealTime') -> bool:
        return self.value < other.value
    
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
        return Time.getBeforeFunArgs("RealTime_"+extra_id, IntSort())