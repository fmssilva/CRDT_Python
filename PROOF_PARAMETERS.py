from CvRDTs.Time.RealTime import RealTime


# Some proofs don't terminate, so one solution is to limite the size of tables to test and accept that limitation
MAX_TABLES_SIZE_TO_PROVE = 100

# choose the "Time" to be used by the tables in the before function
BEFORE_FUNCTION_TIME_TYPE = RealTime

# choose max number of replicas (for VersionVector)
NUMBER_OF_REPLICAS = 3


