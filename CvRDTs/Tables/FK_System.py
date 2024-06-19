from abc import abstractmethod
from typing import Dict, List, Tuple
from z3 import *
from z3 import BoolRef

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Tables.DWFlags import DWFlags
from CvRDTs.Tables.Flags_Constants import Status
from CvRDTs.Tables.PK import PK
from CvRDTs.Tables.Table import Table



class FK_System(CvRDT['FK_System']): 
    ''' generic class for FK_Systems to extend.'''

    def __init__(self, main_table, ref_tables: List[Table], ref_FK_Systems: List['FK_System'] = []):
        self.main_table = main_table # the main table of this system, for example AlbunsTable, in a Albuns_FK_System
        self.ref_tables = ref_tables # the simple tables to which the element references; example Album has a FK to ArtistTable
        self.ref_FK_Systems = ref_FK_Systems # the FK_Systems to which the element references; example Album has a FK to Country_FK_System, and that country has a FK to Continent_FK_System
    
    @abstractmethod
    def merge(self, that: 'FK_System') -> 'FK_System':
        pass

    def reachable(self) -> BoolRef:
        return And(
            self.main_table.reachable(),
            And(*[ref_table.reachable() for ref_table in self.ref_tables]),
            And(*[ref_FK_System.reachable() for ref_FK_System in self.ref_FK_Systems])
        )
  
    def equals(self, other: 'FK_System') -> BoolRef:
        return And(
            self.main_table.equals(other.main_table),
            And(*[ref_table.equals(other.ref_table) for ref_table, other.ref_table in zip(self.ref_tables, other.ref_tables)]),
            And(*[ref_FK_System.equals(other.ref_FK_System) for ref_FK_System, other.ref_FK_System in zip(self.ref_FK_Systems, other.ref_FK_Systems)])
        )
    
    def __eq__(self, other: 'FK_System') -> BoolRef:
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.'''
        return And(
            self.main_table.pure_equals(other.main_table),
            And(*[ref_table.__eq__(other.ref_table) for ref_table, other.ref_table in zip(self.ref_tables, other.ref_tables)]),
            And(*[ref_FK_System.__eq__(other.ref_FK_System) for ref_FK_System, other.ref_FK_System in zip(self.ref_FK_Systems, other.ref_FK_Systems)])
        )

    def compare(self, that: 'FK_System') -> BoolRef:
        return And(
            self.main_table.compare(that.main_table),
            And(*[ref_table.compare(that.ref_table) for ref_table, that.ref_table in zip(self.ref_tables, that.ref_tables)]),
            And(*[ref_FK_System.compare(that.ref_FK_System) for ref_FK_System, that.ref_FK_System in zip(self.ref_FK_Systems, that.ref_FK_Systems)])
        )
    
    def compatible(self, that: 'FK_System') -> BoolRef:
        return And(
            self.main_table.compatible(that.main_table),
            And(*[ref_table.compatible(that.ref_table) for ref_table, that.ref_table in zip(self.ref_tables, that.ref_tables)]),
            And(*[ref_FK_System.compatible(that.ref_FK_System) for ref_FK_System, that.ref_FK_System in zip(self.ref_FK_Systems, that.ref_FK_Systems)])
        )
    
    def ref_integrity_holds_elem(self, pk: PK) -> BoolRef:
        elem = self.main_table.elements.get(pk)
        if (elem == None): # the system does not have this album
            return False 
        # TODO: dp implementar tb UW e fazer aqui um if a distinguir entre DW e UW
        return self.has_visible_fks_versions(elem)


    #######################################################
    ### HELPER METHODS FOR REFERENTIAL INTEGRITY PROOFS  ##
    
    # --->> FOR DELETE-WINS MAIN TABLE 
    def has_visible_fks_versions(self, elem: Tuple[DWFlags, PK]) -> BoolRef:
        ''' return - false if some FK is not visible anymore (the version of the FK in this Album does not match the version of the FK in the original referenced table)
                     (check one FK at a time, so if the first is not visible for example, we don't need to check the others)
                     true if all FKs are still visible
            @Pre: the album with the given PK exists.
            @Pre: this method is only called if the main_table is a DELETE_WINS table.'''
        if is_true(self.main_table.getVersion(elem[1].artFK) != elem[0].get_fk_version(0)):
            self.amortize_path(elem[1].albPK)
            return False
        return True

    def getVersion(self, pk: 'PK') -> int:
        ''' To be called by other FK_Systems which have Albums as FKs
            return the version of the album with the given PK
            @Pre: the album with the given PK exists.
            @Pre: this method is only called if the main_table is a DELETE_WINS table.'''
        elem = self.main_table.elements.get(pk)
        if is_true(elem[0].flag == DWFlags.DELETED):
            return 0
        elif is_true(self.has_visible_fks_versions(elem)):
            return elem[0].version
        else:
            return self.amortize_path(elem[1].alb_pk)
        
    def amortize_path(self, pk: 'PK') -> Int:
        ''' To avoid future searches in all depth of the FKs Tree,
            we set the flag of this album as DELETED
            return 0 to denote that the FKs are not visible anymore.'''
        self.albs_table.setFlag(pk, Status.DELETED)
        return 0

    #######################################################
    ##########      HELPER METHODS FOR PROOFS  ############
    
    @staticmethod
    def getArgs(extra_id: str, tables: List[CvRDT]):
        '''return symbolic all different variables for 3 different instances of the given concrete FK_System, 
            and also list of those variables to be used by Z3.'''
        
        syst1_args, syst2_args, syst3_args = [], [], []
        z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances = [], [], []

        # symbolic variables for 3 different instances of each table of the given concrete FK_System
        for table_name, table_type in tables.items():
            # get args for the table
            tab1_args, tab2_args, tab3_args, tab_vars_for_1_instance, tab_vars_for_2_instances, tab_vars_for_3_instances = table_type.getArgs(table_name + extra_id)

            # create an instance of that table and add to args of the FK_System
            syst1_args.append(table_type(*tab1_args)) # FK_System like Album_FK_System has tables as args, so here we instanciate those tables
            syst2_args.append(table_type(*tab2_args)) # similiar to: FK1_args = [AlbsTable(*albTab1_args), ArtsTable(*artTab1_args)]
            syst3_args.append(table_type(*tab3_args))

            # add the symbolic variables of the table to the list of symbolic variables of the FK_System
            z3_vars_for_1_instance += tab_vars_for_1_instance
            z3_vars_for_2_instances += tab_vars_for_2_instances
            z3_vars_for_3_instances += tab_vars_for_3_instances
        
        return syst1_args, syst2_args, syst3_args, z3_vars_for_1_instance, z3_vars_for_2_instances, z3_vars_for_3_instances
    
    @staticmethod
    def get_RefIntProof_Args(extra_id: str, concrete_FK_System: 'FK_System', concrete_elem_PK: 'PK'):
        '''return symbolic all different variables for 2 different instances of Alb_FK_System and 1 instance of AlbPK, and also list of those variables to be used by Z3.'''

        # symbolic args and variables for 2 instances of FK_System
        FK1_args, FK2_args, _, _, FK_vars_for_2_instances, _ = concrete_FK_System.getArgs(extra_id)

        # symbolic args and variables for 1 instance of AlbPK
        elemPK_args, _, _, elemPK_vars_for_1_instance, _, _ = concrete_elem_PK.getArgs("FK_System"+extra_id)
        
        # List of all symbolic variables for 2 instances of Alb_FK_System and 1 instance of AlbPK
        z3_vars_for_2_instances = FK_vars_for_2_instances + elemPK_vars_for_1_instance

        return FK1_args, FK2_args, elemPK_args, z3_vars_for_2_instances

            
    