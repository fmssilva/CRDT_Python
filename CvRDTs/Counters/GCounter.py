
from z3 import *
from typing import List

from CvRDTs.CvRDT import CvRDT

class GCounter(CvRDT['GCounter']):
    '''A Grow-only Counter (GCounter) is a counter that can only be incremented.
        It is a list of integers, one for each replica in the network.
        It extends CvRDT which accepts a generic type T, which we here bind to GCounter.'''

    def __init__(self, entries: List[Int]):
        self.entries = entries  

    ############################################################################################################
    ##############################  CvRDT methods  #########################################################

    def compatible(self, that: 'GCounter') -> BoolRef:
        return self.network_size() == that.network_size() # vectors with same length

    def reachable(self) -> BoolRef:
        return self.well_formed()

    def __eq__(self, that):
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.'''
        return self.entries == that.entries
    
    # equals implemented in CvRDT class
    # checks if self <= that && that <= self
    # but it's important to check in terms of sum of the vector and not each idx like version vector 
    # TODO: yes??
    
    def compare(self, that):
        return self.value() <= that.value()
    
    def merge(self, that):
        '''@Pre: self.compatible(that)'''
        # we use zip because we know self.compatible(that) and so we know each arg is in the right position of the list, and that the lists have the same length
        merged_entries = [If(e1 > e2, e1, e2) for e1, e2 in zip(self.entries, that.entries)]
        return GCounter(merged_entries)
        
    
    ############################################################################################################
    ##############################  GCounter methods  #########################################################

    def network_size(self):
        return len(self.entries)

    def well_formed(self):
        return And(*[And (isinstance(entry, int), entry >= 0) for entry in self.entries])

    def value(self):
        return self.compute_value()

    def compute_value(self, sum=0, replica=0):
        if 0 <= replica < len(self.entries):
            return self.compute_value(sum + self.entries[replica], replica + 1)
        else:
            return sum

    def increment(self, replica, value) -> None:
        # TODO: need to check this
        assert 0 <= replica < len(self.entries), "Replica index out of range"
        self.entries[replica] += value
        
    def value_of_entry(self, idx):
        assert 0 <= idx < len(self.entries), "GCounter - Entry index out of range"
        return self.entries[idx]


    @staticmethod
    def getArgs(extra_id: str,  totReplicas = 5):
        '''return symbolic all different variables for 3 different instances of GCounter, and also list of those variables to be used by Z3.'''

        # symbolic varibales for 3 different instances of GCounter
        GC1_entries = [Int(f'GC1_entry_{i}_{extra_id}') for i in range(totReplicas)] # each entry must have a different name so we use i to differentiate them
        GC2_entries = [Int(f'GC2_entry_{i}_{extra_id}') for i in range(totReplicas)] # and to differentiate for each GC we use GC1, GC2, GC3
        GC3_entries = [Int(f'GC3_entry_{i}_{extra_id}') for i in range(totReplicas)]
        
        GC1_args = [GC1_entries] # we put a list inside a list [[]] so then *args will unpack and use the inner list as simple arg
        GC2_args = [GC2_entries]
        GC3_args = [GC3_entries]

        z3_vars_for_instance1 = GC1_entries
        z3_vars_for_instance2 = GC2_entries
        z3_vars_for_instance3 = GC3_entries
        
        return GC1_args, GC2_args, GC3_args, z3_vars_for_instance1, z3_vars_for_instance2, z3_vars_for_instance3
    