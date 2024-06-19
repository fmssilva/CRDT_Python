
from z3 import *
from typing import List

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Tables.Flags_Constants import Status, Version

class DWFlags(CvRDT['DWFlags']):
    '''DWFlags is a CvRDT that represents the flags of a table element.
       It has a version, a flag and a list of foreign keys versions.
       It extends CvRDT which accepts a generic type T, which we here bind to DWFlags.'''

    def __init__(self, version: int, flag: int, fk_versions: List[int]):
        self.version = version
        self.flag = flag
        self.fk_versions = fk_versions

    def compatible(self, that: 'DWFlags') -> BoolRef:
        return len(self.fk_versions) == len(that.fk_versions)

    def reachable(self) -> BoolRef:
        return And( self.version >= Version.INIT_VERSION,
                    Or (self.flag == Status.DELETED, self.flag == Status.VISIBLE),
                    And(*[fk_version >= Version.INIT_VERSION for fk_version in self.fk_versions])
        )
    
    def __eq__(self, that: 'DWFlags') -> BoolRef:
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.
            @Pre: self.compatible(that)'''
        return And(
            self.version == that.version,
            self.flag == that.flag,
            And(*[fk1 == fk2 for fk1, fk2 in zip(self.fk_versions, that.fk_versions)])
        )

    # def equals(self, that: 'DWFlags') -> BoolRef:
    #     ''' When comparing CvRDT objects, we want to check if they are equal according to the `compare` method.
    #           CvRDT equals: return True if (this <= that && that <= this).
    #         But for better efficiency we can override equals directly and check if each field (this == that), instead of testing (this <= that && that <= this).'''
    #     return self.__eq__(that)

    def compare(self, that: 'DWFlags') -> BoolRef:
        '''Returns True if `self`<=`that`.
            If "equals" is implemented directly, this compare will not be used.'''
        return And(
            self.version <= that.version,
            # TODO: convém VISIBLE ser menor que DELETED?
            self.flag >= that.flag,
            And(*[fk1 <= fk2 for fk1, fk2 in zip(self.fk_versions, that.fk_versions)])
        )


    def merge(self, that: 'DWFlags') -> 'DWFlags':
        # If different versions -> choose the bigger one
        merged_version = If(self.version > that.version, self.version, that.version)
        
        # Merge flags: if different versions -> choose the flag of the bigger one; if same version -> if equal flags -> one; if different flags -> choose the DELETED one 
        merged_flag = If(self.version > that.version, self.flag,
               If(that.version > self.version, that.flag, 
                  If(self.flag == that.flag, self.flag, 
                     If (self.flag == Status.DELETED, self.flag, that.flag))))

        # If same version and same flag -> merge fk_versions choosing the bigger one
        # TODO - ver como melhorar eficiencia 
        merged_fk_versions = [If(self.version > that.version, fk1, 
                                 If (that.version > self.version, fk2,
                                     If (fk1 > fk2, fk1, fk2))) for fk1, fk2 in zip(self.fk_versions, that.fk_versions)]

        return DWFlags(merged_version, merged_flag, merged_fk_versions)
        
    


    ############################################################################################################
    #      Helper methods to be called by FK_System
    ############################################################################################################

    def get_fk_version(self, idx: int) -> Int:
        return self.fk_versions[idx]

    def set_flag(self, new_flag: Int) -> 'DWFlags':
        return DWFlags(self.version, new_flag, self.fk_versions)




    ############################################################################################################
    #      Helper methods for the Proofs
    ############################################################################################################

    @staticmethod
    def getArgs(extra_id: str, tot_FKs:int):
        '''return symbolic all different variables for 3 different instances of DWFlags, and also list of those variables to be used by Z3.'''
        
        # symbolic varibales for 3 different instances of DWFlags
        version1, version2, version3 = Ints(f'version1_{extra_id} version2_{extra_id} version3_{extra_id}')
        
        flag1, flag2, flag3 = Ints(f'flag1_{extra_id} flag2_{extra_id} flag3_{extra_id}')
        
        fk_version1 = [Int(f'fk_versions1_{i}_{extra_id}') for i in range(tot_FKs)]
        fk_version2 = [Int(f'fk_versions2_{i}_{extra_id}') for i in range(tot_FKs)]
        fk_version3 = [Int(f'fk_versions3_{i}_{extra_id}') for i in range(tot_FKs)]

        DWFlags1_args = [version1, flag1, fk_version1]
        DWFlags2_args = [version2, flag2, fk_version2]
        DWFlags3_args = [version3, flag3, fk_version3]

        z3_vars_for_1_instance = [version1, flag1] + fk_version1
        z3_vars_for_2_instances = z3_vars_for_1_instance + [version2, flag2] + fk_version2
        z3_vars_for_3_instances = z3_vars_for_2_instances + [version3, flag3] + fk_version3
        
        return DWFlags1_args, DWFlags2_args, DWFlags3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
    