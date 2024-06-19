
from z3 import *
from typing import TypeVar, Generic

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.LamportClock import LamportClock

V = TypeVar('V')

class LWWRegister(Generic[V], CvRDT['LWWRegister[V]']):
    '''LWWRegister is a CvRDT that represents a Last-Write-Wins Register.
        It has a value and a timestamp.
        It extends CvRDT which accepts a generic type T, which we here bind to LWWRegister[V].'''
    

    def __init__(self, value: V, stamp: 'LamportClock'):
        self.value = value
        self.stamp = stamp

    def get_value(self) -> V:
        return self.value

    def assign(self, value: V, timestamp: 'LamportClock') -> 'LWWRegister[V]':
        return LWWRegister(value, timestamp)

    def merge(self, that: 'LWWRegister[V]') -> 'LWWRegister[V]':
        if is_true(self.stamp.greater_or_equal(that.stamp)):
            return self
        return that

    def compare(self, that: 'LWWRegister[V]') -> BoolRef:
        return self.stamp.smaller_or_equal(that.stamp)

    def __eq__(self, that: 'LWWRegister[V]') -> BoolRef:
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.'''
        return And(self.value == that.value, self.stamp.__eq__(that.stamp))

    def compatible(self, that: 'LWWRegister[V]') -> BoolRef:
        return Implies(self.stamp == that.stamp, self.value == that.value)


    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of LWWRegister, and also list of those variables to be used by Z3.'''

        # symbolic varibales for 3 different instances of LWWRegister
        value1, value2, value3 = Ints(f'LWW_value1_{extra_id} LWW_value2_{extra_id} LWW_value3_{extra_id}')
        lc1_args, lc2_args, lc3_args, lc_vars_for_1_instance, lc_vars_for_2_instances, lc_vars_for_3_instances = LamportClock.getArgs("LWW_" + extra_id)

        lww1_args = [value1, LamportClock(*lc1_args)]
        lww2_args = [value2, LamportClock(*lc2_args)]
        lww3_args = [value3, LamportClock(*lc3_args)]
        
        z3_vars_for_1_instance = [value1] + lc_vars_for_1_instance
        z3_vars_for_2_instances = [value1, value2] + lc_vars_for_2_instances
        z3_vars_for_3_instances = [value1, value2, value3] + lc_vars_for_3_instances

        return lww1_args, lww2_args, lww3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
    