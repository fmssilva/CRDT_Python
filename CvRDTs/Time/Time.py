

from abc import abstractmethod

from CvRDTs.CvRDT import CvRDT


class Time(CvRDT['Time']):
    '''Time is an abstract class defining the method that all concrete "clocks" must implement.'''
        
    @abstractmethod
    def before(self, other: 'Time') -> bool:
        pass

