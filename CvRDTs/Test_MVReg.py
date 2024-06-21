from typing import Set, Tuple
from z3 import *

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.RealTime import RealTime
from CvRDTs.Time.Time import Time

class Test_MVReg (CvRDT['TestClass']):
    ''' This is a temporary class to build the MVRegister step by step.'''


    def __init__(self, times: Set[Tuple[int,Time]] = None):
        self.times = times or set()

    def reachable(self) -> BoolRef:
        # print("reachable")
        # print(        
        # And (*[Or(t1 == t2, t1.before(t2)) for t1 in self.times for t2 in self.times])
        # )
        # exit()

        return True

    def compatible(self, that: 'Test_MVReg') -> BoolRef:
        return True


    def compare(self, that: 'Test_MVReg') -> BoolRef:
        # print("compare")
        # print(self.times.before(that.times))
        # exit()
        return self.times <= that.times
    
    def __eq__(self, that: 'Test_MVReg') -> bool:
        return self.times == that.times


    def merge(self, that: 'Test_MVReg') -> 'Test_MVReg':
        print("merge")
        
        merged_set = set()
        for tup1 in self.times:
            for tup2 in that.times:
                merged_set.add(If(tup1[1].before(tup2[1]), 1, False))

        exit()
        return Test_MVReg(max(self.times, that.times))
    
    @staticmethod
    def getArgs(extra_id: str):

        # time: Time

        t1_1_args, t1_2_args, t1_3_args, vars_for_t1_1, vars_for_t1_2, vars_for_t1_3 = RealTime.getArgs("t1_"+extra_id)
        t2_1_args, t2_2_args, t2_3_args, vars_for_t2_1, vars_for_t2_2, vars_for_t2_3 = RealTime.getArgs("t2_"+extra_id)
        t3_1_args, t3_2_args, t3_3_args, vars_for_t3_1, vars_for_t3_2, vars_for_t3_3 = RealTime.getArgs("t3_"+extra_id)
        
        v1_1, v1_2, v1_3 = Ints('v1_1 v1_2 v1_3')
        v2_1, v2_2, v2_3 = Ints('v2_1 v2_2 v2_3')
        v3_1, v3_2, v3_3 = Ints('v3_1 v3_2 v3_3')

        set1 = set([(v1_1, RealTime(*t1_1_args)), (v1_2, RealTime(*t1_2_args)), (v1_3, RealTime(*t1_3_args))])
        set2 = set([(v2_1, RealTime(*t2_1_args)), (v2_2, RealTime(*t2_2_args)), (v2_3, RealTime(*t2_3_args))])
        set3 = set([(v3_1, RealTime(*t3_1_args)), (v3_2, RealTime(*t3_2_args)), (v3_3, RealTime(*t3_3_args))])
                    
        test1_args = [set1]
        test2_args = [set2]
        test3_args = [set3]

        vars_for_test1 = vars_for_t1_1 + vars_for_t2_1 + vars_for_t3_1 + [v1_1, v2_1, v3_1]
        vars_for_test2 = vars_for_t1_2 + vars_for_t2_2 + vars_for_t3_2 + [v1_2, v2_2, v3_2]
        vars_for_test3 = vars_for_t1_3 + vars_for_t2_3 + vars_for_t3_3 + [v1_3, v2_3, v3_3]

        return test1_args, test2_args, test3_args, vars_for_test1, vars_for_test2, vars_for_test3



        