
from z3 import *
from typing import List

# import Proofs
from CvRDTs.Proofs_CvRDTs import Proofs_CvRDT
from CvRDTs.Proofs_Ref_Integrity import Proofs_Ref_Integrity

# import CvRDTs
from CvRDTs.Time.LamportClock import LamportClock
from CvRDTs.Time.VersionVector import VersionVector
from CvRDTs.Registers.LWWRegister import LWWRegister
from CvRDTs.Counters.GCounter import GCounter
from CvRDTs.Tables.DWFlags import DWFlags

# import ConcreteTables
from ConcreteTables.Art import Art, ArtsTable
from ConcreteTables.Alb import Alb, Alb_FK_System, AlbPK, AlbsTable



#####################################################################
############   STEP 1 ->>  CHOOSE PROOF PARAMETERS        ###########
'''In PROOF_PARAMETERS.py file, set the proof parameters to use.'''



#####################################################################
#############  STEP 1 ->>       CHOOSE PROOF TO RUN        ##########
'''Choose: a) The CvRDT to prove;   b) The type of proof to run.'''

CvRDT_TO_PROVE = 53
CvRDT_options = {   
        # Time:
            1: LamportClock, 2: VersionVector,
        # Counters:
            11: GCounter, 
        # Registers:
            21: LWWRegister,
        # Tables:
            31: DWFlags, 
            41: Art, 42: ArtsTable,
            51: Alb, 52: AlbsTable, 53: Alb_FK_System
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
############   STEP 1 ->>  RUN THE SCRIPT        ############
#############################################################






#############################################################
#################       HELPER METHOD      ##################

def print_proof(proof_name, solver):
    res = solver.check()
    print(f"\n{CvRDT_to_prove.__name__}: {proof_name} - holds ?  ", (res == sat))
    if res == sat:
        print("sat model:   ", solver.model())
    elif res == unsat:
        print("unsat core:   ", solver.unsat_core())
    else:
        print("unknown result")
    solver.reset() # Reset solver to clean the previous constraints 

def check_all_z3_variables_have_different_names(vars_for_3_instances: List[str]):
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
    proofs = Proofs_CvRDT()
    arg_for_getArgs = ["",50] if (CvRDT_to_prove == DWFlags or CvRDT_to_prove == VersionVector )else [""]
    instance1_args, instance2_args, instance3_args, vars_for_1_instance, vars_for_2_instances, vars_for_3_instances = CvRDT_to_prove.getArgs(*arg_for_getArgs)
    check_all_z3_variables_have_different_names(vars_for_3_instances)

    if proof_to_run in ["compare_correct", "ALL"]:
        solver.add(
            proofs.compare_correct(
                vars_for_2_instances,
                CvRDT_to_prove(*instance1_args), CvRDT_to_prove(*instance2_args)))
        print_proof("compare_correct", solver)
    
    if proof_to_run in ["is_a_CvRDT"]:
        solver.add(
            proofs.is_a_CvRDT(
                vars_for_3_instances,
                CvRDT_to_prove(*instance1_args), CvRDT_to_prove(*instance2_args), CvRDT_to_prove(*instance3_args)))
        print_proof("is_a_CvRDT", solver)
    
    if proof_to_run in ["compatible_commutes", "ALL"]:
        solver.add(
            proofs.compatible_commutes(
                vars_for_2_instances,
                CvRDT_to_prove(*instance1_args), CvRDT_to_prove(*instance2_args)))
        print_proof("compatible_commutes", solver)

    if proof_to_run in ["merge_idempotent", "ALL"]:
        solver.add(
            proofs.merge_idempotent(
                vars_for_1_instance,
                CvRDT_to_prove(*instance1_args)))
        print_proof("merge_idempotent", solver)

    if proof_to_run in ["merge_commutative", "ALL"]:
        solver.add(
            proofs.merge_commutative(
                vars_for_2_instances,
                CvRDT_to_prove(*instance1_args), CvRDT_to_prove(*instance2_args)))
        print_proof("merge_commutative", solver)

    if proof_to_run in ["merge_associative", "ALL"]:
        solver.add(
            proofs.merge_associative(
                vars_for_3_instances,
                CvRDT_to_prove(*instance1_args), CvRDT_to_prove(*instance2_args), CvRDT_to_prove(*instance3_args)))
        print_proof("merge_associative", solver)

    if proof_to_run in ["merge_reachable", "ALL"]:
        solver.add(
            proofs.merge_reachable(
                vars_for_3_instances,
                CvRDT_to_prove(*instance1_args), CvRDT_to_prove(*instance2_args), CvRDT_to_prove(*instance3_args)))
        print_proof("merge_reachable", solver)

    if proof_to_run in ["merge_compatible", "ALL"]:
        solver.add(
            proofs.merge_compatible(
                vars_for_3_instances,
                CvRDT_to_prove(*instance1_args), CvRDT_to_prove(*instance2_args), CvRDT_to_prove(*instance3_args)))
        print_proof("merge_compatible", solver)
    
    # Now we'll run the Ref_Integrity_Proofs, but only if the CvRDT_to_prove is a FK_System:
    if CvRDT_to_prove == Alb_FK_System:
        print("\n\n\nStarting Ref_Integrity proofs for ", CvRDT_to_prove.__name__)

        proofs = Proofs_Ref_Integrity()
        FK1_args, FK2_args, albPK_args, vars_for_2_inst_of_FK_Syst_and_1_inst_of_its_PKs = CvRDT_to_prove.get_RefIntProof_Args("")
        check_all_z3_variables_have_different_names(vars_for_2_inst_of_FK_Syst_and_1_inst_of_its_PKs)

        if proof_to_run in ["generic_referential_integrity", "ALL"]:
            solver.add(
                proofs.generic_referential_integrity(
                    vars_for_2_inst_of_FK_Syst_and_1_inst_of_its_PKs,
                    CvRDT_to_prove(*FK1_args), CvRDT_to_prove(*FK2_args), AlbPK(*albPK_args)))
            print_proof("generic_referential_integrity", solver)

