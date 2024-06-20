
from z3 import *
from typing import Tuple, Set, Callable, TypeVar

from z3 import BoolRef

from CvRDTs.CvRDT import CvRDT
from CvRDTs.Time.RealTime import RealTime
from CvRDTs.Time.Time import Time

V = TypeVar('V')


class MVRegister(CvRDT['MVRegister']):

    def __init__(self, before_fun: Callable[[Time, Time], bool], values: Set[Tuple[V, Time]] = None):
        self.before_fun = before_fun
        self.value_time_tuples = values or set()

    ###############################################################
    #####################  CvRDT Methods  #########################

    def compatible(self, that: 'MVRegister') -> BoolRef:
        ''' replicas must have the same notion of time.'''
        return self.before_fun == that.before_fun
    
    def reachable(self) -> BoolRef:
        # reachable usando um Time em vez de before
        print(And (*[tup1[1].before(tup2[1]) for tup1 in self.value_time_tuples for tup2 in self.value_time_tuples]))
        exit()
        
        # choose the reachable method to 
        
        

        return self.reachable_without_time(self.before_fun) 
        # return self.reachable_gen_time()
    

    def reachable_without_time(self, beforeF: Callable[[Time, Time], bool]) -> bool:
        booleans = []
        
        for tup1 in self.value_time_tuples:
            for tup2 in self.value_time_tuples:
                self.before(tup1[1], tup2[1])

                exit()
                print (tup1[0], tup1[1], tup2[0], tup2[1])
                booleans.append(Or(tup1[1] == tup2[1], tup1[1].before(tup2[1])))
        exit()
        return And(self.before_fun == beforeF,
                all(Or(t1[1] == t2[1], self.concurrent(t1[1], t2[1]))
                    for t1 in self.value_time_tuples for t2 in self.value_time_tuples))


    def reachable_gen_time(self) -> BoolRef:
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
        for (v1, time1) in self.value_time_tuples:
            for (v2, time2) in self.value_time_tuples:
                s.add(Or(time1 == time2, self.concurrent(time1, time2)))

        # Check the satisfiability of the constraints
        return s.check() == sat
    

    def before(self, t1: 'Time', t2: 'Time') -> BoolRef:
        # TODO ????
        return t1.before(t2) 
    
    def concurrent(self, t1: 'Time', t2: 'Time') -> BoolRef:
        return And (t1 != t2, 
                    Not(self.before(t1, t2)), 
                    Not(self.before(t2, t1)))



    def __eq__(self, that: 'MVRegister') -> BoolRef:
        return And (self.before_fun == that.before_fun, 
                    self.value_time_tuples == that.value_time_tuples) # this == will check if all elements of this and that set match, and for each element, in this case Tuple(v,time), check if they are ==, and if v is of primitive type so its a normal ==, else if v is some object then will be compared by __eq__, and same for time, which must implement its __eq__ in its class
        
    # equals defined in CvRDT which calls compare to check if this <= that and that <= this

    def compare(self, that: 'MVRegister') -> BoolRef:
        booleans = []
        for v1, t1 in self.value_time_tuples:
            res = And(*[And(v1 == v2, t1.before(t2)) for v2, t2 in that.value_time_tuples])
            exit()
            print(v1, t1)
            found_match = Or([And(sym_vars[v1, t1], sym_vars[v2, t2]) for v2, t2 in set2 if v1 == v2 and t1 == t2])
        s.add(found_match)

        exit()


        print(x[1])
        
        exit()

        print(self.value_time_tuples[0][1])

        return all(x[1].before_or_equal(y[1]) for x in self.value_time_tuples for y in that.value_time_tuples)

    def merge(self, that: 'MVRegister') -> 'MVRegister':
        self_latest_values = self.keep_latest(that)
        that_latest_values = that.keep_latest(self)
        merged_values = self_latest_values.union(that_latest_values)
        return MVRegister(self.before_fun, merged_values)



    ###############################################################
    #####################  MVRegister Methods  #####################

    def keep_latest(self, that: 'MVRegister') -> Set[Tuple[V, Time]]:
        '''keep values of self that are concurrent or bigger than values of that.'''
        set_to_keep = set()
        intersection = self.value_time_tuples.intersection(that.value_time_tuples)    
        # for x in self.values:
        #     for y in that.values:
        return self.value_time_tuples.intersection(that.value_time_tuples) # TO CORRECT 
        #         if x[0] == y[0]:
        #             set_to_keep.add( x if Or(self.concurrent(x[1], y[1]), self.after_or_equal(x[1], y[1])) ))
        # return set_to_keep
    
        return {x for x in self.value_time_tuples if
                all(Or (self.concurrent(x[1], y[1]), self.after_or_equal(x[1], y[1])) for y in that.value_time_tuples)}

    def assign(self, v, timestamp):
        new_value = self.value_time_tuples.copy()
        new_value.add((v, timestamp))
        return MVRegister(self.before_fun, new_value)

    def assign_many(self, vs: Set, timestamp):
        stamped_values = {(v, timestamp) for v in vs}
        return MVRegister(self.before_fun, stamped_values)

    def value(self) -> Set:
        return {v for (v, _) in self.value_time_tuples}

    def contains(self, e) -> bool:
        return any(x[0] == e for x in self.value_time_tuples)



    ###############################################################
    #####################  Methods for Proofs  ####################
    
    @staticmethod
    def getArgs (extra_id: str, max_values_per_reg: int = 1, clock: Time = RealTime):
        '''return symbolic all different variables for 3 different instances of a given concrete table, and also list of those variables to be used by Z3.'''

        # before: Callable[[Time, Time], bool]
        before_args1, before_args2, before_args3, before_args_for_instance1, before_args_for_instance2, before_args_for_instance3 = clock.getBeforeFunArgs("MVReg_"+extra_id)

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

        args1 = before_args1 + [set1]
        args2 = before_args2 + [set2]
        args3 = before_args3 + [set3]

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


