
from z3 import *
from typing import Tuple, Set, Callable, TypeVar

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.Time import Time
from PROOF_PARAMETERS import BEFORE_FUNCTION_TIME_TYPE, MAX_TABLES_SIZE_TO_PROVE

V = TypeVar('V')


class MVRegister(CvRDT['MVRegister']):

    def __init__(self, before: Callable[[Time, Time], bool], values: Set[Tuple[V, Time]] = None):
        self.before = before
        self.values = values or set()

    ###############################################################
    #####################  CvRDT Methods  #########################

    def compatible(self, that: 'MVRegister') -> BoolRef:
        ''' replicas must have the same notion of time.'''
        return self.before == that.before
    

    def reachable(self) -> BoolRef:
        ''' We don't want to check our MVRegister with a specific Time type, 
                example RealTime or VersionVector which have their different implementation of before function.
            Instead we let each concrete Time do its implementation, 
                and we just check our MVRegister with a generic before function,
                and we just add some constraints for the before function's, of the properties that all of them must have.
            Having our generic before function, we can check if our MVRegister is reachable for any Time type.'''

        s = Solver()
        t1, t2, t3 = Ints('t1 t2 t3') # 3 symbolic variables for time

        # Add constraints for the before function's properties
        before = Function('before', IntSort(), IntSort(), BoolSort())

        s.add(ForAll([t1], Not(before(t1, t1))))
        s.add(ForAll([t1, t2], Implies(before(t1, t2), Not(before(t2, t1)))))
        s.add(ForAll([t1, t2, t3], Implies(And(before(t1, t2), before(t2, t3)), before(t1, t3))))

        # Add constraints for the values set
        for (v1, time1) in self.values:
            for (v2, time2) in self.values:
                s.add(Or(time1 == time2, self.concurrent(time1, time2)))

        # Check the satisfiability of the constraints
        return s.check() == sat
    


    def __eq__(self, that: 'MVRegister') -> BoolRef:
        return And (self.before == that.before, 
                    self.values == that.values) # this == will check if all elements of this and that set match, and for each element, in this case Tuple(v,time), check if they are ==, and if v is of primitive type so its a normal ==, else if v is some object then will be compared by __eq__, and same for time, which must implement its __eq__ in its class
        

    # equals defined in CvRDT which calls compare to check if this <= that and that <= this

    def compare(self, that: 'MVRegister') -> BoolRef:
        return all(self.before_or_equal(x[1], y[1]) for x in self.values for y in that.values)

    def merge(self, that: 'MVRegister') -> 'MVRegister':
        self_latest_values = self.keep_latest(that)
        that_latest_values = that.keep_latest(self)
        merged_values = self_latest_values.union(that_latest_values)
        return MVRegister(self.before, merged_values)



    ###############################################################
    #####################  MVRegister Methods  #####################

    def before(self, t1, t2):
        return self.before(t1, t2) # and this before function must be implemented in the concrete Time classes

    def before_or_equal(self, t1, t2):
        return self.before(t1, t2) or t1 == t2

    def after_or_equal(self, t1, t2):
        return self.before(t2, t1) or t1 == t2

    def concurrent(self, t1, t2):
        return not self.before(t1, t2) and not self.before(t2, t1) and t1 != t2

    def keep_latest(self, that):
        return {x for x in self.values if
                all(self.concurrent(x[1], y[1]) or self.after_or_equal(x[1], y[1]) for y in that.values)}

    def assign(self, v, timestamp):
        new_value = self.values.copy()
        new_value.add((v, timestamp))
        return MVRegister(self.before, new_value)

    def assign_many(self, vs: Set, timestamp):
        stamped_values = {(v, timestamp) for v in vs}
        return MVRegister(self.before, stamped_values)

    def value(self) -> Set:
        return {v for (v, _) in self.values}


    def contains(self, e) -> bool:
        return any(x[0] == e for x in self.values)

    def reachable_without_time(self, beforeF: Callable[[Time, Time], bool]) -> bool:
        return (self.before == beforeF and
                all(self.concurrent(t1[1], t2[1]) or t1[1] == t2[1]
                    for t1 in self.values for t2 in self.values))


    ###############################################################
    #####################  Methods for Proofs  ####################
    
    @staticmethod
    def getArgs (extra_id: str, max_values_per_reg: int = 1):
        '''return symbolic all different variables for 3 different instances of a given concrete table, and also list of those variables to be used by Z3.'''

        # before: Callable[[Time, Time], bool]
        before_args1, before_args2, before_args3, before_args_for_instance1, before_args_for_instance2, before_args_for_instance3 = BEFORE_FUNCTION_TIME_TYPE.getBeforeFunArgs("MVReg_"+extra_id)

        # values: Set[Tuple[V, Time]]    
        set1_values = [Int(f'set1_value{i}_{extra_id}') for i in range(max_values_per_reg)]
        set2_values = [Int(f'set2_value{i}_{extra_id}') for i in range(max_values_per_reg)]
        set3_values = [Int(f'set3_value{i}_{extra_id}') for i in range(max_values_per_reg)]

        set1_times = [Int(f'set1_time{i}_{extra_id}') for i in range(max_values_per_reg)]
        set2_times = [Int(f'set2_time{i}_{extra_id}') for i in range(max_values_per_reg)]
        set3_times = [Int(f'set3_time{i}_{extra_id}') for i in range(max_values_per_reg)]

        set1 = set([(v, t) for v, t in zip(set1_values, set1_times)])
        set2 = set([(v, t) for v, t in zip(set2_values, set2_times)])
        set3 = set([(v, t) for v, t in zip(set3_values, set3_times)])

        args1 = [before_args1, set1]
        args2 = [before_args2, set2]
        args3 = [before_args3, set3]

        vars_for_instance1 = set1_values + set1_times + before_args_for_instance1
        vars_for_instance2 = set2_values + set2_times + before_args_for_instance2
        vars_for_instance3 = set3_values + set3_times + before_args_for_instance3

        return args1, args2, args3, vars_for_instance1, vars_for_instance2, vars_for_instance3


        ####################################################################
        # WITH TIME

        # vars_for_instance1, vars_for_instance2, vars_for_instance3 = [], [], []

        # set1, set2, set3 = set(), set(), set()
        
        # for tupl in range(max_values_per_reg): # for each Tuple(V, Time) in the set of each replica
            
        #     # get symbolic variables for Time for each replica
        #     clock1_args, clock2_args, clock3_args, clock_vars_for_instance1, clock_vars_for_instance2, clock_vars_for_instance3 = clock.getArgs(f"tupl{tupl}_MVreg_{extra_id}")
            
        #     # get symbolic variables for V for each replica
        #     v1, v2, v3 = Ints(f'tupl{tupl}_MVReg1_{extra_id} tupl{tupl}_MVReg2_{extra_id} tupl{tupl}_MVReg3_{extra_id}')
                            
        #     set1.add( (v1, clock(*clock1_args)) )
        #     set2.add( (v2, clock(*clock2_args)) )
        #     set3.add( (v3, clock(*clock3_args)) )

        #     vars_for_instance1 += [v1] + clock_vars_for_instance1 
        #     vars_for_instance2 += [v2] + clock_vars_for_instance2
        #     vars_for_instance3 += [v3] + clock_vars_for_instance3

        # MVreg1_args = [clock, set1]
        # MVreg2_args = [clock, set2]
        # MVreg3_args = [clock, set3]

        # return MVreg1_args, MVreg2_args, MVreg3_args, vars_for_instance1, vars_for_instance2, vars_for_instance3


