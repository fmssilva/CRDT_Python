
from z3 import *

from CvRDTs.CvRDT import CvRDT
from PROOF_PARAMETERS import NUMBER_OF_REPLICAS 

class VersionVector(CvRDT['VersionVector']):
    
    def __init__(self, vector):
        self.vector = vector
    
    ########################################################################
    ###################         CvRDT methods         ######################

    def compatible(self, that: 'VersionVector') -> BoolRef:
        return And (self.networkSize() == that.networkSize()) # this checks if vectors have same size

    def reachable(self):
        return And( self.networkSize() == NUMBER_OF_REPLICAS,
                    self.wellFormed()) 

    def __eq__(self, that: 'VersionVector') -> BoolRef:
        return And(self.vector == that.vector)
        
    # equals = this <= that && that <= this implemented in CvRDT class
        
    def compare(self, that: 'VersionVector') -> BoolRef:
        return self.beforeOrEqual(that)
    
    def merge(self, that: 'VersionVector') -> 'VersionVector':
        return self.sync(that)

    ######################################################################
    #################       VersionVector Operations       ###############
    
    def wellFormedWithSize(self) -> BoolRef:
        return And(len(self.vector) == NUMBER_OF_REPLICAS, self.wellFormed())
    
    def wellFormed(self) -> BoolRef:
        ''' it's not necessary for vectors start in 0, but it's more logical and easier to understand. 
            Also it's important that every idx has an int value and is not None.'''
        return And(*[And(isinstance(v, int), v >= 0) for v in self.vector])
    
    def networkSize(self) -> int:
        return len(self.vector)

    def increment(self, replica: int) -> 'VersionVector':
        new_vector = self.vector[:] # copy by value (shallow copy)
        new_vector[replica] += 1
        return VersionVector(new_vector)

    def before(self, that: 'VersionVector') -> BoolRef:
        # we can use zip because we know each idx corresponds to the same replica, and also vectors have the same size so there will be no elements left in the longest vector)
        vectors = zip(self.vector, that.vector)
        return And(
            And(*[a <= b for a, b in vectors]), # all values <= 
            Or(*[a < b for a, b in vectors]))   # && exists at least one value <

    def beforeOrEqual(self, that: 'VersionVector') -> BoolRef:
        # return Or(self.vector == that.vector, self.before(that))
        # to be more efficient we can check directly:
        return And(*[a <= b for a, b in zip(self.vector, that.vector)])

    def after(self, that: 'VersionVector') -> BoolRef:
        return that.before(self)

    def afterOrEqual(self, that: 'VersionVector') -> BoolRef:
        # return Or(self.vector == that.vector, self.after(that))
        # to be more efficient we can check directly:
        return And(*[a >= b for a, b in zip(self.vector, that.vector)])

    def concurrent(self, that: 'VersionVector') -> BoolRef:
        return And(self.vector != that.vector, # if they are equal, it represents the same state, so they are not concurrent
                   Not(self.before(that)),
                   Not (that.before(self)))

    def sync(self, that) -> 'VersionVector':
        # we can use zip because we know each idx corresponds to the same replica, and also vectors have the same size so there will be no elements left in the longest vector)
        new_vector = [If(a >= b, a, b) for a, b in zip(self.vector, that.vector)]
        return VersionVector(new_vector)

    







    ########################################################################
    ###################         Helper methods         ######################
    @staticmethod
    def getArgs(extra_id: str, totReplicas: int):
        '''return symbolic all different variables for 3 different instances of VersionVector, and also list of those variables to be used by Z3.'''

        # symbolic varibales for 3 different instances of VersionVector
        vector1 = [Int(f'vectVersion1_{i}_{extra_id}') for i in range(totReplicas)]
        vector2 = [Int(f'vectVersion2_{i}_{extra_id}') for i in range(totReplicas)]
        vector3 = [Int(f'vectVersion3_{i}_{extra_id}') for i in range(totReplicas)]

        vec1_args = [vector1]
        vec2_args = [vector2]
        vec3_args = [vector3]

        z3_vars_for_instance1 = vector1
        z3_vars_for_instance2 = vector2
        z3_vars_for_instance3 = vector3

        return vec1_args, vec2_args, vec3_args, z3_vars_for_instance1, z3_vars_for_instance2, z3_vars_for_instance3