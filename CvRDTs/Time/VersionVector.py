from z3 import *
from z3 import BoolRef

from CvRDTs.CvRDT import CvRDT
from PROOF_PARAMETERS import NUMBER_OF_REPLICAS 

class VersionVector(CvRDT['VersionVector']):
    
    def __init__(self, vector):
        self.vector = vector
    
    def __eq__(self, that: 'VersionVector') -> BoolRef:
        return And(self.vector == that.vector)
            # self.reachable(), that.reachable(),
            # self.compatible(that),
            # *[a == b for a, b in zip(self.vector, that.vector)])
        
    ########################################################################
    ###################         CvRDT methods         ######################

    def equals (self, that: 'VersionVector') -> bool:
        '''@Pre: self.compatible(that)'''
        return self.compare(that), that.compare(self)

    def compare(self, that: 'VersionVector') -> BoolRef:
        return self.beforeOrEqual(that)
    
    def compatible(self, that: 'VersionVector') -> BoolRef:
        return And (self.networkSize() == that.networkSize(),
                    self.wellFormedWithSize(), that.wellFormedWithSize())
    
    def reachable(self):
        '''@Pre: self.compatible(that)'''
        return And( self.networkSize() == NUMBER_OF_REPLICAS,
                    *[v >= 0 for v in self.vector])
    
    def merge(self, that: 'VersionVector') -> 'VersionVector':
        return self.sync(that)

    ######################################################################
    #################       VersionVector Operations       ###############

    def networkSize(self) -> int:
        return len(self.vector)
    
    def wellFormedWithSize(self) -> BoolRef:
        return And(len(self.vector) == NUMBER_OF_REPLICAS, self.wellFormed())
    
    def wellFormed(self) -> BoolRef:
        return And(*[And(isinstance(v, int), v >= 0) for v in self.vector])
    


    def increment(self, replica: int) -> 'VersionVector':
        new_vector = self.vector[:] # copy by value (shallow copy)
        new_vector[replica] += 1
        return VersionVector(new_vector)

    def before(self, that: 'VersionVector') -> BoolRef:
        vectors = zip(self.vector, that.vector)
        return And(
            And(*[a <= b for a, b in vectors]), # all values <= 
            Or(*[a < b for a, b in vectors]))   # && exists at least one value <

    def beforeOrEqual(self, that: 'VersionVector') -> BoolRef:
        return Or(self.vector == that.vector, self.before(that))

    def after(self, that: 'VersionVector') -> BoolRef:
        return that.before(self)

    def afterOrEqual(self, that: 'VersionVector') -> BoolRef:
        return Or(self.vector == that.vector, self.after(that))

    def concurrent(self, that: 'VersionVector') -> BoolRef:
        return And(self.vector != that.vector,
                   Not(self.before(that)),
                   Not (that.before(self)))

    def sync(self, that) -> 'VersionVector':
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

        vv1_args = [vector1]
        vv2_args = [vector2]
        vv3_args = [vector3]

        z3_vars_for_1_instance = vector1
        z3_vars_for_2_instances = vector1 + vector2
        z3_vars_for_3_instances = vector1 + vector2 + vector3

        return vv1_args, vv2_args, vv3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances