
from z3 import *

from CvRDTs.Time.Time import Time


class IntTime(Time):
    '''A class to represent a time as an integer value. extends Time abstract class.'''

    def __init__(self, value: Int):
        self.value = value

    def before(self, other: 'IntTime') -> bool:
        '''@Pre: other is an instance of IntTime'''
        return self.value < other.value

    
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
        