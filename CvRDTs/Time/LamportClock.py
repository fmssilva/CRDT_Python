
from z3 import *

from CvRDTs.CvRDT import CvRDT

class LamportClock(CvRDT['LamportClock']):
    '''Lamport Clock does not converge, we always increment the counter.
        Nevertheless, we extend CvRDT so we can test some propoerties with Z3.
        CvRDT accepts a generic type T, which we here bind to LamportClock.'''

    def __init__(self, replica: Int, counter: Int):
        self.replica = replica
        self.counter = counter

    def increment(self) -> 'LamportClock':
        return LamportClock(self.replica, self.counter + 1)

    def sync(self, that: 'LamportClock') -> 'LamportClock':
        max_time = If(self.counter >= that.counter, self.counter, that.counter)
        return LamportClock(self.replica, max_time + 1)

    def smaller(self, that: 'LamportClock') -> BoolRef: # impose a total order using the replica id
        return Or(self.counter < that.counter, And(self.counter == that.counter, self.replica < that.replica))

    def smaller_or_equal(self, that: 'LamportClock') -> BoolRef:
        return Or(self == that, self.smaller(that))

    def greater_or_equal(self, that: 'LamportClock') -> BoolRef:
        return Not(self.smaller(that))
    
    def compare(self, that: 'LamportClock') -> BoolRef:
        return self.smaller_or_equal(that)
    
    def merge(self, that: 'LamportClock') -> 'LamportClock':
        return self.sync(that)

    def __eq__(self, that: 'LamportClock') -> BoolRef:
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.'''
        return And(self.replica == that.replica, self.counter == that.counter)

    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of LamportClock, and also list of those variables to be used by Z3.'''

        # symbolic varibales for 3 different instances of LamportClock
        replica1, replica2, replica3 = Ints(f'replica1_{extra_id} replica2_{extra_id} replica3_{extra_id}')
        counter1, counter2, counter3 = Ints(f'counter1_{extra_id} counter2_{extra_id} counter3_{extra_id}')
        
        LC1_args = [replica1, counter1]
        LC2_args = [replica2, counter2]
        LC3_args = [replica3, counter3]

        z3_vars_for_1_instance = [replica1, counter1]
        z3_vars_for_2_instances = [replica1, counter1, replica2, counter2]
        z3_vars_for_3_instances = [replica1, counter1, replica2, counter2, replica3, counter3]

        return LC1_args, LC2_args, LC3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
    