
from z3 import *
from z3 import BoolRef

from CvRDTs.CvRDT import CvRDT

class LamportClock(CvRDT['LamportClock']):
    '''Lamport Clock does not converge, we always increment the counter.
        Nevertheless, we extend CvRDT so we can test some propoerties with Z3.
        CvRDT accepts a generic type T, which we here bind to LamportClock.'''

    def __init__(self, replica: int, counter: int):
        self.replica = replica
        self.counter = counter

    ########################################################################
    ################       CvRDT methods       #############################

    # compatible is True

    def reachable(self) -> BoolRef:
        '''it's not necessary to have positive values for replica and counter, but it's more logical.'''
        return And (self.replica >= 0, self.counter >= 0)
    
    def __eq__(self, that: 'LamportClock') -> BoolRef:
        '''@Pre: self.compatible(that)'''
        return And(self.replica == that.replica, self.counter == that.counter)

    # equals is as defined in CvRDT

    def compare(self, that: 'LamportClock') -> BoolRef:
        return self.smaller_or_equal(that)
    
    def merge(self, that: 'LamportClock') -> 'LamportClock':
        return self.sync(that)


    ########################################################################
    ################       LamportClock methods       ######################

    def increment(self) -> 'LamportClock':
        return LamportClock(self.replica, self.counter + 1)

    def sync(self, that: 'LamportClock') -> 'LamportClock':
        max_time = If(self.counter >= that.counter, self.counter, that.counter)
        return LamportClock(self.replica, max_time + 1)
        # if want to try LamportClock as a CvRDT, converging, then use the next lines:
        # max_replica = If(self.replica >= that.replica, self.replica, that.replica)
        # return LamportClock(max_replica, max_time)
    
    def smaller(self, that: 'LamportClock') -> BoolRef: # impose a total order using the replica id
        return Or(And(self.counter == that.counter, self.replica < that.replica), self.counter < that.counter)

    def smaller_or_equal(self, that: 'LamportClock') -> BoolRef:
        return Or(self == that, self.smaller(that))

    def greater_or_equal(self, that: 'LamportClock') -> BoolRef:
        return Not(self.smaller(that))
    
    def getGreateOrEqualStamp(self, that: 'LamportClock') -> 'LamportClock':
        rep = If(self.greater_or_equal(that), self.replica, that.replica)
        count = If(self.greater_or_equal(that), self.counter, that.counter)
        return LamportClock(rep, count)
    
    
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
    