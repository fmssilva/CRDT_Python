
from typing import Tuple
from z3 import *
from abc import abstractmethod

from CvRDTs.CvRDT import CvRDT


class Time(CvRDT['Time']):
    '''Time is an abstract class defining the method that all concrete "clocks" must implement.'''
        
    @abstractmethod
    def before(self, other: 'Time') -> bool:
        pass

    def before_or_equal(self, other: 'Time') -> BoolRef:
        return Or(self == other, self.before(other))

    def after_or_equal(self, other: 'Time') -> BoolRef:
        return Or(self == other, other.before(self))

    def concurrent(self, other: 'Time') -> BoolRef:
        return And (self != other, 
                    Not(self.before(other)), 
                    Not(other.before(self)))


    @staticmethod
    def getBeforeFunArgs(extra_id: str, arg_type: SortRef, return_type: SortRef = BoolSort()):
        
        # 3 symbolic "before" functions
        before1_args = [Function(f'before1_{extra_id}', arg_type, arg_type, return_type)] 
        before2_args = [Function(f'before2_{extra_id}', arg_type, arg_type, return_type)] 
        before3_args = [Function(f'before3_{extra_id}', arg_type, arg_type, return_type)] 

        # Symbolic variables for the args of the functions
        bef1_var1, bef1_var2, bef2_var1, bef2_var2, bef3_var1, bef3_var2 = Ints(f'RealTime1_before1_{extra_id} RealTime2_before1_{extra_id} RealTime1_before2_{extra_id} RealTime2_before2_{extra_id} RealTime1_before3_{extra_id} RealTime2_before3_{extra_id}')
                                                  
        z3_vars_for_before1 = [bef1_var1, bef1_var2]
        z3_vars_for_before2 = [bef2_var1, bef2_var2]
        z3_vars_for_before3 = [bef3_var1, bef3_var2]

        return before1_args, before2_args, before3_args, z3_vars_for_before1, z3_vars_for_before2, z3_vars_for_before3