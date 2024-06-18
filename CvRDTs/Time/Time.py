

from abc import ABC, abstractmethod


class Time(ABC):
    '''Time is an abstract class defining the method that all concrete "clocks" must implement.'''
        
    @abstractmethod
    def before(self, other: 'Time') -> bool:
        pass

