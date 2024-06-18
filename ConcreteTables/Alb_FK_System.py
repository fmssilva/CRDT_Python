
from typing import Tuple
from z3 import *

from ConcreteTables.Alb import Alb, AlbPK
from CvRDTs.CvRDT import CvRDT
from ConcreteTables.AlbsTable import AlbsTable
from ConcreteTables.ArtsTable import ArtsTable
from CvRDTs.Tables.DWFlags import DWFlags


class Alb_FK_System(CvRDT['Alb_FK_System']):
    '''A class to represent an Alb_FK_System. It has 2 attributes: albs_table and arts_table.
        Extends CvRDT, and CvRDT accepts a generic type T, which we here bind to Alb_FK_System.'''
         
    def __init__(self, albs_table: AlbsTable, arts_table: ArtsTable):
        self.albs_table = albs_table
        self.arts_table = arts_table

    def reachable(self) -> BoolRef:
        return And(
            self.albs_table.reachable(),
            self.arts_table.reachable(),
            And(*[self.has_visible_fks_versions(elem)
                  for elem in self.albs_table.elements.values()])
        )

    def equals(self, other: 'Alb_FK_System') -> BoolRef:
        return And(
            self.albs_table.equals(other.albs_table),
            self.arts_table.equals(other.arts_table)
        )

    def compare(self, other: 'Alb_FK_System') -> BoolRef:
        return And(
            self.albs_table.compare(other.albs_table),
            self.arts_table.compare(other.arts_table)
        )

    def compatible(self, other: 'Alb_FK_System') -> BoolRef:
        return And(
            self.albs_table.compatible(other.albs_table),
            self.arts_table.compatible(other.arts_table)
        )

    def merge(self, other: 'Alb_FK_System') -> 'Alb_FK_System':
        return Alb_FK_System(
            self.albs_table.merge(other.albs_table),
            self.arts_table.merge(other.arts_table)
        )


    #################################################################
    ##############      Helper methods      #########################

    def amortize_path(self, pk: 'AlbPK') -> Int:
        ''' To avoid future searches in all depth of the FKs Tree,
            we set the flag of this album as DELETED
            return 0 to denote that the FKs are not visible anymore.'''
        self.albs_table.setFlag(pk, DWFlags.DELETED)
        return 0


    def has_visible_fks_versions(self, elem: Tuple[DWFlags, Alb]) -> BoolRef:
        ''' return - false if some FK is not visible anymore (the version of the FK in this Album does not match the version of the FK in the original referenced table)
                     (check one FK at a time, so if the first is not visible for example, we don't need to check the others)
                     true if all FKs are still visible
            @Pre: the album with the given PK exists.'''
        if is_true(self.arts_table.getVersion(elem[1].artFK) != elem[0].get_fk_version(0)):
            self.amortize_path(elem[1].albPK)
            return False
        return True



    def getVersion(self, pk: 'AlbPK') -> int:
        ''' To be called by other FK_Systems which have Albums as FKs
            return the version of the album with the given PK
            @Pre: the album with the given PK exists.'''
        elem = self.albs_table.elements.get(pk)
        if is_true(elem[0].flag == DWFlags.DELETED):
            return 0
        elif is_true(self.has_visible_fks_versions(elem)):
            return elem[0].version
        else:
            return self.amortize_path(elem[1].alb_pk)



    def ref_integrity_holds_elem(self, pk: AlbPK) -> BoolRef:
        elem = self.albs_table.elements.get(pk)
        if (elem == None): # the system does not have this album
            return False 
        return self.has_visible_fks_versions(elem)


    @staticmethod
    def getArgs(extra_id: str):
        '''return symbolic all different variables for 3 different instances of Alb_FK_System, and also list of those variables to be used by Z3.'''
        # symbolic varibales for 3 different instances of Alb_FK_System
        albTab1_args, albTab2_args, albTab3_args, albTab_vars_for_1_instance, albTab_vars_for_2_instances, albTab_vars_for_3_instances = AlbsTable.getArgs(extra_id+"FK_System")
        artTab1_args, artTab2_args, artTab3_args, artTab_vars_for_1_instance, artTab_vars_for_2_instances, artTab_vars_for_3_instances = ArtsTable.getArgs(extra_id+"FK_System")

        FK1_args = [AlbsTable(*albTab1_args), ArtsTable(*artTab1_args)]
        FK2_args = [AlbsTable(*albTab2_args), ArtsTable(*artTab2_args)]
        FK3_args = [AlbsTable(*albTab3_args), ArtsTable(*artTab3_args)]

        z3_vars_for_1_instance = albTab_vars_for_1_instance + artTab_vars_for_1_instance
        z3_vars_for_2_instances = albTab_vars_for_2_instances + artTab_vars_for_2_instances
        z3_vars_for_3_instances = albTab_vars_for_3_instances + artTab_vars_for_3_instances

        return FK1_args, FK2_args, FK3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
        

    @staticmethod
    def get_RefIntProof_Args(extra_id: str):
        '''return symbolic all different variables for 2 different instances of Alb_FK_System and 1 instance of AlbPK, and also list of those variables to be used by Z3.'''

        # symbolic args and variables for 2 instances of Alb_FK_System
        FK1_args, FK2_args, _, _, FK_vars_for_2_instances, _ = Alb_FK_System.getArgs(extra_id)

        # symbolic args and variables for 1 instance of AlbPK
        albPK_args, _, _, albPK_vars_for_1_instance, _, _ = AlbPK.getArgs(extra_id+"FK_System")
        
        # List of all symbolic variables for 2 instances of Alb_FK_System and 1 instance of AlbPK
        z3_vars_for_2_instances = FK_vars_for_2_instances + albPK_vars_for_1_instance

        return FK1_args, FK2_args, albPK_args, z3_vars_for_2_instances
