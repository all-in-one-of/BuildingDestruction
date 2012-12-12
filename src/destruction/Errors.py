'''
Created on Oct 18, 2011

@author: carlos
'''
import traceback
import logging

class Error(Exception):
    """Base class for exceptions in this module."""
    @staticmethod
    def display_exception(e):
        logging.error('Exception ocurred:' + e.expr)
        print 'Exception ocurred:', e.expr
        traceback.print_exc()

class CantBeNoneError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class NegativeValueError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class TransitionError(Error):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        prev -- state at beginning of transition
        next -- attempted new state
        msg  -- explanation of why the specific transition is not allowed
    """

    def __init__(self, prev, next, msg):
        self.prev = prev
        self.next = next
        self.msg = msg
