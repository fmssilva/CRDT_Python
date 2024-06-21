
# To run proofs install Z3:

    pip install z3-solver   

# Run each document of the z3_examples folder
    - examples from the basic to the more complex to understand how z3 works 
    - the document: "ex_2_4_CvRDT_example_of_APP_implementation"
        has an implementation with the same structure as the global APP, 
        so it's a good document to see first to understand how the APP is structured

# Run CvRDT Proofs: 
    - Doc: "main_proofs": 
        - At the beginning of the doc, there are a couple of options you can choose of test to run
    - Folder: ConcreteTables
        - Has the documents of the concrete implementations of the DB
            each document, for example, Alb, has the implementation for
                - AlbPK, Alb, AlbTable, and Alb_FK_System
    - Folder CvRDTs: 
        - CvRDT.py with the methods every CvRDT must implement for us to run the proofs 
        - Proofs_CvRDT.py with the concrete proofs to run in Z3 to prove that it is a CvRDT (merge idempotent, commutative, associative...)
        - Proofs_Ref_Integrity.py with concrete proof to run in Z3 to prove that a FK_System holds the referential integrity
        - sub-folders - with implementations of different types of CvRDTs 
            - Counters
            - Registers
            - Tables
            - Time 
                - Time.py is an abstract class that every concrete implementation like version vector, real-time, etc. must extend
                    this way all our CvRDTs that receive some Time as argument, we can do it easily, without much generic types
                    