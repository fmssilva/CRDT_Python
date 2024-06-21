
from z3 import *
from typing import List

# import Proofs
from ConcreteTables.Country import CountriesTable, Country
from ConcreteTables.Genre import Genre, GenreTable
from ConcreteTables.Song import Song, SongsTable
from CvRDTs.Proofs_CvRDTs import Proofs_CvRDT
from CvRDTs.Proofs_Ref_Integrity import Proofs_Ref_Integrity

# import CvRDTs
from CvRDTs.Counters.GCounter import GCounter
from CvRDTs.Registers.MVRegister import MVRegister
from CvRDTs.Tables.FK_System import FK_System
from CvRDTs.Tables.Table import Table
from CvRDTs.Tables.Flags_UW import Flags_UW
from CvRDTs.Tables.Flags_DW import Flags_DW
from CvRDTs.Test_MVReg import Test_MVReg
from CvRDTs.Time.RealTime import RealTime
from CvRDTs.Time.LamportClock import LamportClock
from CvRDTs.Time.VersionVector import VersionVector
from CvRDTs.Registers.LWWRegister import LWWRegister

# import ConcreteTables
from ConcreteTables.Art import Art, Art_FK_System, ArtsTable
from ConcreteTables.Alb import Alb, Alb_FK_System, AlbPK, AlbsTable



#####################################################################
############   STEP 1 ->>  CHOOSE PROOF PARAMETERS        ###########

TABLE_SIZE_FOR_SYMBOLIC_VARS = 200
# Size of table to fill with symbolic variables. When preparing proofs to run in Z3 we need to set up some symbolic variables for all our attributes, fields, objects, etc. With complex examples the number of symbolic variables to test rise fast. So set here the size of tables to fill with symbolic variables 

VECTOR_SIZE_FOR_SYMBOLIC_VARS = 50          
# Size of vector of DWFlag (fk_versions) and MVRegister set(Tuple(v, time)), to fill with symbolic variables.

DEFAULT_TIME = VersionVector             
# "Time" to be used by the tables and MVRegister in the before function

#############################################################
############   STEP 2 ->>  CHOOSE TABLES POLICIES    ########
''' in "ConcreteTables" folder we have the documents for each table (Art, Alb, etc.)
        - each document includes the elemPK, element, elemTable and elem_FK_system if there is any.
    So to change the policy of some class, from "UW" to "DW" or vice-versa: 
        - do Ctrl+F "DW" in de document, and "replace all" to "DW"
          and the code will be already good to run, with the correct imports and types'''

# TODO: IMPORTANT!!!
    # UW Tables need to be confirmed correctness
    # FK_System for now is just implementing DW policy, 
    #   -> need to divide in FK_System_UW and FK_System_DW to have the diffrente specific implementations
    


#####################################################################
#############  STEP 3 ->>       CHOOSE PROOF TO RUN        ##########
'''Choose: a) The CvRDT to prove;   b) The type of proof to run.'''

CvRDT_TO_PROVE = 83
CvRDT_options = { 
        # Class for testing simple codes... 
            0: Test_MVReg, # TODO: this is a class just for simple testing of some syntax... might not run at any moment 
        # Time:
            1: LamportClock, # --> THIS IS NOT A CvRDT - It always grows in each merge.)
            2: VersionVector,       # TESTS OK 
            3: RealTime,            # TESTS OK BUT -> TODO: Flags_UW does not merge idempotent with real time, need to check what's wrong
        # Counters:
            11: GCounter,                       # TESTS OK
        # Registers:
            21: LWWRegister,                    # TESTS OK
            22: MVRegister,     # TODO - with Z3 it's hard to use data structures inside other data structures like set(Tuple(v, time))
                                #       - need to be implemented, maybe creating a simple Tuple class so then we can go down that level to execute the correct comparisons using Z3 If, which should have primitives as return types If (condition, primitiveA, primitiveB) 
        # Tables:
            31: Flags_DW,       # TESTS OK
            32: Flags_UW,       # TESTS OK  BUT TODO: with RealTime clock it's not merge idempotent, need to check what's wrong
            41: Country, 42: CountriesTable,    # TESTS OK -> currently DW policy
            51: Genre, 52: GenreTable,          # TESTS OK -> currently UW policy
            61: Art, 62: ArtsTable, 63: Art_FK_System,  # TESTS OK  -> currently UW
                                                # TODO -> it is running with UW Table, but the FK_System itself still DW. need to implement UW
            71: Song, 72: SongsTable,           # TESTS OK -> currently DW policy
            81: Alb, 82: AlbsTable, 83: Alb_FK_System # TESTS OK -> currently DW policy

}

PROOF_TO_RUN = 1
proofs_options = {  
        # CvRDTProofs:
            1: "ALL", 
            2: "compare_correct", 
            3: "is_a_CvRDT",  # This proof is too big for complex cases. So we will only run it if you choose it specifically. In "ALL" option we'll run instead the parts of it separately, enumerated below.
                #  is_a_CvRDT proof divided in parts to run with "ALL" option 
                4: "compatible_commutes", 
                5: "merge_idempotent", 6: "merge_commutative", 
                7: "merge_associative", 8: "merge_reachable", 
                9: "merge_compatible",
        # Ref_Integrity_Proofs:
            10: "generic_referential_integrity"
}

#############################################################
############   STEP 4 ->>  RUN THE SCRIPT        ############
#############################################################






#############################################################
#################       HELPER METHOD      ##################

def getArgsForProof():
    ''' To run each CvRDT through the z3 proofs we need to prepare those objects 
        with different arguments and symbolic variables.So for us to ask the class to prepare those, 
        we need to pass different args for its method getArgs().'''
    if CvRDT_to_prove == Flags_DW:
        return ["",VECTOR_SIZE_FOR_SYMBOLIC_VARS]
    if CvRDT_to_prove == Flags_UW:
        return ["", DEFAULT_TIME]
    if CvRDT_to_prove == MVRegister:
        return ["", VECTOR_SIZE_FOR_SYMBOLIC_VARS, DEFAULT_TIME]
    if issubclass(CvRDT_to_prove, Table) or issubclass(CvRDT_to_prove, FK_System):
        return ["",TABLE_SIZE_FOR_SYMBOLIC_VARS, DEFAULT_TIME]
    return [""]



def print_proof(proof_name, solver):
    # TODO: implement the automatic negation of the proof for as to run again and then show the counter example
    res = solver.check()
    print(f"{CvRDT_to_prove.__name__}: {proof_name}\t- holds ?", (res == sat))
    # if res == sat:
    #     print("sat model:   ", solver.model())
    # elif res == unsat:
    #     print("unsat core:   ", solver.unsat_core())
    # else:
    #     print("unknown result")
    solver.reset() # Reset solver to clean the previous constraints 


def check_all_z3_variables_have_different_names(vars_for_3_instances: List[str]):
    ''' All the z3 symbolic variables for z3 must have different names for a correct proof.
        So we check it here.'''
    if len(set(vars_for_3_instances)) == len(vars_for_3_instances):
        print("\nCorrect symbolic variable names (all variables have different names for Z3 proofs)")
    else:
        print("ERROR: All variables must be different for Z3 proofs.")
        seen_vars = set()
        duplicates = list()
        for var in vars_for_3_instances:
            if var in seen_vars:
                duplicates.append(var)    
            seen_vars.add(var)
        print("Duplicates:\n", duplicates)
        exit()
 


#############################################################
###################          MAIN        ####################

if __name__ == "__main__":

    solver = Solver()

    CvRDT_to_prove = CvRDT_options[CvRDT_TO_PROVE]
    proof_to_run = proofs_options[PROOF_TO_RUN]
    
    print("\n\n\n\n\n\nStarting CvRDT proofs for ", CvRDT_to_prove.__name__)
    
    proofs = Proofs_CvRDT

    arg_for_getArgs = getArgsForProof()    
    instance1_args, instance2_args, instance3_args, vars_for_instance1, vars_for_instance2, vars_for_instance3 = CvRDT_to_prove.getArgs(*arg_for_getArgs)
    vars_for_2_instances = vars_for_instance1 + vars_for_instance2
    vars_for_3_instances = vars_for_instance1 + vars_for_instance2 + vars_for_instance3
    check_all_z3_variables_have_different_names(vars_for_3_instances)

    instance1 = CvRDT_to_prove(*instance1_args)
    instance2 = CvRDT_to_prove(*instance2_args)
    instance3 = CvRDT_to_prove(*instance3_args)


    if proof_to_run in ["compare_correct", "ALL"]:
        solver.add(proofs.compare_correct(vars_for_2_instances,instance1, instance2))
        print_proof("compare_correct", solver)
    
    if proof_to_run in ["is_a_CvRDT"]:
        solver.add(proofs.is_a_CvRDT(vars_for_3_instances, instance1, instance2, instance3))
        print_proof("is_a_CvRDT", solver)
    
    if proof_to_run in ["compatible_commutes", "ALL"]:
        solver.add(proofs.compatible_commutes(vars_for_2_instances, instance1, instance2))
        print_proof("compatible_commutes", solver)

    if proof_to_run in ["merge_idempotent", "ALL"]:
        solver.add(proofs.merge_idempotent(vars_for_instance1, instance1))
        print_proof("merge_idempotent", solver)

    if proof_to_run in ["merge_commutative", "ALL"]:
        solver.add(proofs.merge_commutative(vars_for_2_instances, instance1, instance2))
        print_proof("merge_commutative", solver)

    if proof_to_run in ["merge_associative", "ALL"]:
        solver.add(proofs.merge_associative(vars_for_3_instances, instance1, instance2, instance3))
        print_proof("merge_associative", solver)

    if proof_to_run in ["merge_reachable", "ALL"]:
        solver.add(proofs.merge_reachable(vars_for_3_instances, instance1, instance2, instance3))
        print_proof("merge_reachable", solver)

    if proof_to_run in ["merge_compatible", "ALL"]:
        solver.add(proofs.merge_compatible(vars_for_3_instances, instance1, instance2, instance3))
        print_proof("merge_compatible", solver)
    
    # Now we'll run the Ref_Integrity_Proofs, but only if the CvRDT_to_prove is a FK_System:
    
    # TODO: check when UW and DW FK_Systems are done if we need to adapt this code
    
    if issubclass(CvRDT_to_prove, FK_System):
        print("\nStarting Ref_Integrity proofs for ", CvRDT_to_prove.__name__)

        proofs = Proofs_Ref_Integrity
        FK1_args, FK2_args, elemPK_args, elem_pk_class, vars_for_2_inst_of_FK_Syst_and_1_inst_of_its_PKs = CvRDT_to_prove.get_RefIntProof_Args("",TABLE_SIZE_FOR_SYMBOLIC_VARS, DEFAULT_TIME)

        check_all_z3_variables_have_different_names(vars_for_2_inst_of_FK_Syst_and_1_inst_of_its_PKs)

        fk_syst_instance1 = CvRDT_to_prove(*FK1_args)
        fk_syst_instance2 = CvRDT_to_prove(*FK2_args)
        elem_pk_instance = elem_pk_class(*elemPK_args)
        if proof_to_run in ["generic_referential_integrity", "ALL"]:
            solver.add(proofs.generic_referential_integrity(
                    vars_for_2_inst_of_FK_Syst_and_1_inst_of_its_PKs,
                    fk_syst_instance1, fk_syst_instance2, elem_pk_instance))
            print_proof("generic_referential_integrity", solver)

print("\n")
