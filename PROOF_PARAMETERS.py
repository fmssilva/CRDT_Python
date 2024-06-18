from CvRDTs.Time.IntTime import IntTime


# Some proofs don't terminate, so one solution is to limite the size of tables to test and accept that limitation
MAX_TABLES_SIZE_TO_PROVE = 8

# choose the "Time" to be used by the tables in the before function
BEFORE_FUNCTION_TIME_TYPE = IntTime

# choose max number of replicas (for VersionVector)
MAX_NUM_OF_REPLICAS = 3


