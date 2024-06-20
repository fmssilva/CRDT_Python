
from z3 import *
from typing import TypeVar, Generic

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.LamportClock import LamportClock

V = TypeVar('V')

class LWWRegister(Generic[V], CvRDT['LWWRegister[V]']):
    '''LWWRegister is a CvRDT that represents a Last-Write-Wins Register.
        It has a value and a timestamp.
        It extends CvRDT which accepts a generic type T, which we here bind to LWWRegister[V].
        The generic V value, can be any type, but just primitive types, because if not we might need to implement a reachable method to check conditions for that type.'''
    
    def __init__(self, value: V, stamp: 'LamportClock'):
        self.value = value
        self.stamp = stamp

    ########################################################################
    ################       CvRDT methods       #############################

    def compatible(self, that: 'LWWRegister[V]') -> BoolRef:
        return Implies(self.stamp == that.stamp, self.value == that.value)

    # reachable is True (the values should be of primitive type and can have any value)

    def __eq__(self, that: 'LWWRegister[V]') -> BoolRef:
        ''' Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.
            @Pre: self.compatible(that)'''
        return And(self.value == that.value, self.stamp == that.stamp) # we can use == operator because we implemented __eq__ in LamportClock
    
    # equals is as defined in CvRDT

    def compare(self, that: 'LWWRegister[V]') -> BoolRef:
        return self.stamp.smaller_or_equal(that.stamp)

    def merge(self, that: 'LWWRegister[V]') -> 'LWWRegister[V]':
        merged_value = If(self.stamp.greater_or_equal(that.stamp), self.value, that.value)
        stamp = self.stamp.getGreateOrEqualStamp(that.stamp)
        return LWWRegister(merged_value, stamp)

    
    ########################################################################
    ################       LWWRegister methods       ######################

    def get_value(self) -> V:
        return self.value

    def assign(self, value: V, timestamp: 'LamportClock') -> 'LWWRegister[V]':
        return LWWRegister(value, timestamp)


    def merge_with_version(self, that: 'LWWRegister[V]', this_version: int, that_version: int) -> 'LWWRegister[V]':
        merged_value = If(this_version > that_version, self.value, 
                          If (that_version > this_version, that.value,
                                If (self.stamp.greater_or_equal(that.stamp), self.value, that.value)))
        merged_stamp = self.stamp.merge_with_version(that.stamp, this_version, that_version)
        return LWWRegister(merged_value, merged_stamp)

    ########################################################################
    ################       Proofs Helper Method       ######################

    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of LWWRegister, and also list of those variables to be used by Z3.'''

        # symbolic varibales for 3 different instances of LWWRegister
        value1, value2, value3 = Ints(f'LWW_value1_{extra_id} LWW_value2_{extra_id} LWW_value3_{extra_id}')
        lc1_args, lc2_args, lc3_args, lc_vars_for_instance1, lc_vars_for_instance2, lc_vars_for_instance3 = LamportClock.getArgs("LWW_" + extra_id)

        lww1_args = [value1, LamportClock(*lc1_args)]
        lww2_args = [value2, LamportClock(*lc2_args)]
        lww3_args = [value3, LamportClock(*lc3_args)]
        
        z3_vars_for_instance1 = [value1] + lc_vars_for_instance1
        z3_vars_for_instance2 = [value2] + lc_vars_for_instance2
        z3_vars_for_instance3 = [value3] + lc_vars_for_instance3

        return lww1_args, lww2_args, lww3_args, z3_vars_for_instance1, z3_vars_for_instance2, z3_vars_for_instance3 
    