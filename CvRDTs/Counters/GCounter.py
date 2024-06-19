
from z3 import *
from typing import List

from CvRDTs.CvRDT import CvRDT

class GCounter(CvRDT['GCounter']):
    '''A Grow-only Counter (GCounter) is a counter that can only be incremented.
        It is a list of integers, one for each replica in the network.
        It extends CvRDT which accepts a generic type T, which we here bind to GCounter.'''

    def __init__(self, entries: List[Int]):
        self.entries = entries  

    def increment(self, replica, value):
        assert 0 <= replica < len(self.entries), "Replica index out of range"
        self.entries[replica] += value
    
    def compute_value(self, sum=0, replica=0):
        if 0 <= replica < len(self.entries):
            return self.compute_value(sum + self.entries[replica], replica + 1)
        else:
            return sum

    def value(self):
        return self.compute_value()

    def value_of_entry(self, idx):
        assert 0 <= idx < len(self.entries), "GCounter - Entry index out of range"
        return self.entries[idx]

    def well_formed(self):
        return And(*[And (isinstance(entry, int), entry >= 0) for entry in self.entries])

    def network_size(self):
        return len(self.entries)

    def merge(self, that):
        assert self.network_size() == that.network_size(), "Network sizes do not match"
        merged_entries = [If(e1 > e2, e1, e2) for e1, e2 in zip(self.entries, that.entries)]
        return GCounter(merged_entries)
        
    def compare(self, that):
        assert self.network_size() == that.network_size(), "Network sizes do not match"
        return And(*[e1 <= e2 for e1, e2 in zip(self.entries, that.entries)])
    
    def __eq__(self, that):
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.'''
        return And(*[e1 == e2 for e1, e2 in zip(self.entries, that.entries)])

    def compatible(self, that: 'GCounter') -> BoolRef:
        return self.network_size() == that.network_size()

    def reachable(self) -> BoolRef:
        return And(*[entry >= 0 for entry in self.entries])

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

        z3_vars_for_1_instance = GC1_entries
        z3_vars_for_2_instances = GC1_entries + GC2_entries
        z3_vars_for_3_instances = GC1_entries + GC2_entries + GC3_entries

        return GC1_args, GC2_args, GC3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
    