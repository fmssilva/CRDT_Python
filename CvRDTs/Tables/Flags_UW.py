
from z3 import *
from typing import List

from CvRDTs.Tables.Flags import Flags, Status, Version
from CvRDTs.Time.Time import Time

class Flags_UW(Flags):

    def __init__(self, DI_flag: int, touch: int, time: Time):
        super().__init__(DI_flag)
        self.touch = touch
        self.time = time

    def compatible(self, that: 'Flags_UW') -> BoolRef:
        return self.time.compatible(that.time)

    def reachable(self) -> BoolRef:
        return And( self.time.reachable(),
                    Or (self.DI_flag == Status.DELETED, self.DI_flag == Status.VISIBLE),
                    self.touch == Status.TOUCHED
                )
    
    def __eq__(self, that: 'Flags_UW') -> BoolRef:
        '''Implement the (==) operator of z3 - compare all fields of the object and guarantee that the object is the same.
            @Pre: self.compatible(that)'''
        return And( self.DI_flag == that.DI_flag,
                    self.touch == that.touch,
                    self.time == that.time
                )            

    def equals(self, that: 'Flags_UW') -> BoolRef:
        ''' override equals from CvRDT:
                - for better efficiency: we check if this == that, instead of checking if this <= that and that <= this.
                - to avoid confusing with the compare method, when checking if self.flag <= that.flag, which might give errors if we change the numbers of the flags in the future.'''
        return And( self.DI_flag == that.DI_flag,
                    self.touch == that.touch,
                    self.time.equals(that.time)
                )

    def merge(self, that: 'Flags_UW') -> 'Flags_UW':
        '''if not concurrent so choose the bigger time; if concurrent, we can only accpet DELETE if we don't have a VISIBLE && a TOUCH.'''
        merged_time = self.time.merge(that.time)
        merged_DI_flag = If(self.time.before(that.time), that.DI_flag,
                            If(that.time.before(self.time), self.DI_flag, 
                                If(And(self.DI_flag == Status.DELETED, that.DI_flag == Status.DELETED, self.touch == Status.NOT_TOUCHED, that.touch == Status.NOT_TOUCHED), Status.DELETED, Status.VISIBLE)))
        merged_touch = If(self.time.before(that.time), that.touch,
                            If(that.time.before(self.time), self.touch, 
                                If(Or(self.touch == Status.TOUCHED, that.touch == Status.TOUCHED), Status.TOUCHED, Status.NOT_TOUCHED)))
        return Flags_UW(merged_DI_flag, merged_touch, merged_time)                          



    ############################################################################################################
    #      Helper methods for the Proofs
    ############################################################################################################

    @staticmethod
    def getArgs(extra_id: str, time:Time):
        '''return symbolic all different variables for 3 different instances of UWFlags, and also list of those variables to be used by Z3.'''
        
        # symbolic varibales for 3 different instances of UWFlags
        flag1, flag2, flag3 = Ints(f'flag1_{extra_id} flag2_{extra_id} flag3_{extra_id}')
        touch1, touch2, touch3 = Ints(f'touch1_{extra_id} touch2_{extra_id} touch3_{extra_id}')

        time1_args, time2_args, time3_args, z3_vars_for_time1, z3_vars_for_time2, z3_vars_for_time3 = time.getArgs(f'time_UWFlags_{extra_id}')

        UWFlags1_args = [flag1, touch1, time(*time1_args)]
        UWFlags2_args = [flag2, touch2, time(*time2_args)]
        UWFlags3_args = [flag3, touch3, time(*time3_args)]

        z3_vars_for_instance1 = [flag1, touch1] + z3_vars_for_time1
        z3_vars_for_instance2 = [flag2, touch2] + z3_vars_for_time2
        z3_vars_for_instance3 = [flag3, touch3] + z3_vars_for_time3
        
        return UWFlags1_args, UWFlags2_args, UWFlags3_args, z3_vars_for_instance1, z3_vars_for_instance2, z3_vars_for_instance3