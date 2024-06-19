
from abc import ABC, abstractmethod
from typing import Generic, List, Tuple, TypeVar
from z3 import *

T = TypeVar('T', bound='CvRDT')  
'''Some methods of this CvRDT class, receive as argument, another CvRDT.
    So when a concrete implementation extends CvRDT, we know that the argument of the method is of the same type as that concrete implementation
    And so the type of this generic T will be that concrete implementation
    So when we implement a concrete CvRDT, we pass that concrete name of class so the TypeVar knows what type to bind to T
        ex: class LWWRegister(Generic[V], CvRDT['LWWRegister[V]']):
            class DWTable(CvRDT['DWTable[PK,V]'], Generic[PK, V]):''' 


class CvRDT(ABC, Generic[T]):
    '''CvRDT defines the methods that all CvRDTs must implement, 
        in order to then be proved by the CvRDTProofs.
        Some methods have a default implementation, others are abstract and must be implemented by the concrete classes.
        Because these proofs will be run by Z3, we use Z3 types (BoolRef, Int, etc) and not python types (bool, int, etc)
        If possible, use always Int instead of str for better performance.'''

    def compatible(self, that: T) -> BoolRef:
        """Exclude replicas that are not compatible."""
        return True
    
    def reachable(self) -> BoolRef:
        """Excludes states that are not reachable in practice."""
        return True
    
    @abstractmethod
    def __eq__(self, that: T) -> bool:
        '''When proving with Z3, we want to check if objects are equal to each other by value, and not by reference. 
            So we need to implement __eq__ methods in each class to override the (==) operator. 
            Because if we don't implement __eq__, so (==) operator will fall back to default python object class __eq__, which compare references in memory if (self is other).
            @Pre: self.compatible(that)'''
        pass

    def equals(self, that: T) -> BoolRef:
        """When comparing CvRDT objects, we want to check if they are equal according to the `compare` method.
            Returns True if (this <= that && that <= this).
            @Pre: self.compatible(that)"""
        return And(isinstance(that, self.__class__),
                   self.compare(that), that.compare(self))
    
    @abstractmethod
    def compare(self, that: T) -> BoolRef: 
        """Returns True if `self`<=`that`."""
        pass
    

    @abstractmethod
    def merge(self, that: T) -> T:
        """Returns the least upper bound (LUB) of `self` and `that`."""
        pass

    

