
from z3 import *
from typing import List

from CvRDTs.Tables.Flags import Flags, Status, Version

class Flags_DW(Flags):

    def __init__(self, version: int, DI_flag: int, fk_versions: List[int]):
        super().__init__(DI_flag)
        self.version = version
        self.fk_versions = fk_versions

    def compatible(self, that: 'Flags_DW') -> BoolRef:
        return len(self.fk_versions) == len(that.fk_versions)

    def reachable(self) -> BoolRef:
        return And( self.version >= Version.INIT_VERSION,
                    Or (self.DI_flag == Status.DELETED, self.DI_flag == Status.VISIBLE),
                    And(*[fk_version >= Version.INIT_VERSION for fk_version in self.fk_versions])
        )
    
    def __eq__(self, that: 'Flags_DW') -> BoolRef:
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.
            @Pre: self.compatible(that)'''
        return And(
            self.version == that.version,
            self.DI_flag == that.DI_flag,
            And(*[fk1 == fk2 for fk1, fk2 in zip(self.fk_versions, that.fk_versions)])
        )

    def equals(self, that: 'Flags_DW') -> BoolRef:
        ''' override equals from CvRDT:
                - for better efficiency: we check if this == that, instead of checking if this <= that and that <= this.
                - to avoid confusing with the compare method, when checking if self.flag <= that.flag, which might give errors if we change the numbers of the flags in the future.'''
        return self.__eq__(that)


    def merge(self, that: 'Flags_DW') -> 'Flags_DW':
        # If different versions -> choose the bigger one
        merged_version = If(self.version > that.version, self.version, that.version)
        
        # Merge flags: if different versions -> choose the flag of the bigger one; if same version -> if equal flags -> one; if different flags -> choose the DELETED one 
        merged_flag = If(self.version > that.version, self.DI_flag,
               If(that.version > self.version, that.DI_flag, 
                  If(self.DI_flag == that.DI_flag, self.DI_flag, 
                     If (self.DI_flag == Status.DELETED, self.DI_flag, that.DI_flag))))

        # If same version and same flag -> merge fk_versions choosing the bigger one
        # TODO - ver como melhorar eficiencia 
        merged_fk_versions = [If(self.version > that.version, fk1, 
                                 If (that.version > self.version, fk2,
                                     If (fk1 > fk2, fk1, fk2))) for fk1, fk2 in zip(self.fk_versions, that.fk_versions)]

        return Flags_DW(merged_version, merged_flag, merged_fk_versions)
        
    


    ############################################################################################################
    #      Helper methods to be called by FK_System
    ############################################################################################################

    def get_fk_version(self, idx: int) -> Int:
        return self.fk_versions[idx]

    def set_flag(self, new_flag: Int) -> 'Flags_DW':
        return Flags_DW(self.version, new_flag, self.fk_versions)




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

        z3_vars_for_instance1 = [version1, flag1] + fk_version1
        z3_vars_for_instance2 = [version2, flag2] + fk_version2
        z3_vars_for_instance3 = [version3, flag3] + fk_version3
        
        return DWFlags1_args, DWFlags2_args, DWFlags3_args, z3_vars_for_instance1, z3_vars_for_instance2, z3_vars_for_instance3 
    