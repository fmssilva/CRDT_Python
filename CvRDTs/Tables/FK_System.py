from z3 import *

from CvRDTs.CvRDT import CvRDT



class FK_Sytem(CvRDT['FK_System']): 
    ''' generic class for FK_Systems to extend.'''

    def __init__(self, main_table, fk_table):
        pass