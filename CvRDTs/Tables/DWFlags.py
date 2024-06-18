
from z3 import *
from typing import List

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Tables.Flags_Constants import Status, Version

class DWFlags(CvRDT['DWFlags']):
    '''DWFlags is a CvRDT that represents the flags of a table element.
       It has a version, a flag and a list of foreign keys versions.
       It extends CvRDT which accepts a generic type T, which we here bind to DWFlags.'''

    def __init__(self, version: Int, flag: Int, fk_versions: List[Int]):
        self.version = version
        self.flag = flag
        self.fk_versions = fk_versions

    def reachable(self) -> BoolRef:
        return And(
            self.version >= Version.INIT_VERSION,
            Or (self.flag == Status.DELETED, self.flag == Status.VISIBLE),
            And(*[fk_version >= Version.INIT_VERSION for fk_version in self.fk_versions])
        )

    def equals(self, that: 'DWFlags') -> BoolRef:
        return And(
            self.version == that.version,
            self.flag == that.flag,
            And(*[fk1 == fk2 for fk1, fk2 in zip(self.fk_versions, that.fk_versions)])
        )

    def compare(self, that: 'DWFlags') -> BoolRef:
        # TODO - mas não é preciso porque fazemos override ao equals
        return False

    def compatible(self, that: 'DWFlags') -> BoolRef:
        return len(self.fk_versions) == len(that.fk_versions)

    def merge(self, that: 'DWFlags') -> 'DWFlags':
        # if different versions -> we choose the bigger one
        if is_true (self.version > that.version):
            return self
        if is_true (that.version > self.version):
            return that
        # if same version and same flag -> we merge the fk_versions choosing the bigger one; if both deleted we still need to merge the fk_versions so the merge is comutative
        if is_true (self.flag == that.flag):
            merged_fk_versions = [If(fk1 > fk2, fk1, fk2) for fk1, fk2 in zip(self.fk_versions, that.fk_versions)]
            return DWFlags(self.version, self.flag, merged_fk_versions)
        # if different flags -> we choose the deleted one
        if is_true (self.flag == Status.DELETED):
            return self
        return that
    


    ############################################################################################################
    #      Helper methods to be called by FK_System
    ############################################################################################################

    def get_fk_version(self, idx: int) -> Int:
        return self.fk_versions[idx]

    def set_flag(self, new_flag: Int) -> 'DWFlags':
        return DWFlags(self.version, new_flag, self.fk_versions)

   
    @staticmethod
    def getArgs(extra_id: str, tot_FKs:int):
        '''return symbolic all different variables for 3 different instances of DWFlags, and also list of those variables to be used by Z3.'''
        
        # symbolic varibales for 3 different instances of DWFlags
        version1, version2, version3 = Ints(f'version1{extra_id} version2{extra_id} version3{extra_id}')
        flag1, flag2, flag3 = Ints(f'flag1{extra_id} flag2{extra_id} flag3{extra_id}')
        fk_version1 = [Int(f'fk_versions1{extra_id}{i}') for i in range(tot_FKs)]
        fk_version2 = [Int(f'fk_versions2{extra_id}{i}') for i in range(tot_FKs)]
        fk_version3 = [Int(f'fk_versions3{extra_id}{i}') for i in range(tot_FKs)]

        DWFlags1_args = [version1, flag1, fk_version1]
        DWFlags2_args = [version2, flag2, fk_version2]
        DWFlags3_args = [version3, flag3, fk_version3]

        z3_vars_for_1_instance = [version1, flag1] + fk_version1
        z3_vars_for_2_instances = [version1, version2, flag1, flag2] + fk_version1 + fk_version2
        z3_vars_for_3_instances = [version1, version2, version3, flag1, flag2, flag3] + fk_version1 + fk_version2 + fk_version3

        return DWFlags1_args, DWFlags2_args, DWFlags3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
    