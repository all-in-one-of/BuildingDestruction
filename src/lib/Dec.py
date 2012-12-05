# -*- coding: utf-8 -*-
import sys
import os
import linecache
'''
@file Dec.py
@brief this file will contain all self-implemented decorators or modified decorators from wiki.
@author Carlos Soriano Sánchez
@date 3/03/2011
@see http://en.wikipedia.org/wiki/Decorator_pattern (accesed 02/03/2011)
'''

class Dec:
    '''
    This class provide a self-implemented decorators.
    How implements it: http://www.artima.com/weblogs/viewpost.jsp?thread=240845 (accesed 02/03/2011)

    Quick list:
    accepts: This decorator provide a type checking of parameters inputs to the function.
    It will work with any classes and also accepts static functions and class functions.

    returns: This decorator provide a type checking of parameters outputs from the function.
    It will work with any classes and also accepts static functions and class functions.
    _________________________________

    WARNING: be careful with staticmethod and classmethod decorators provided by python, they will must
    be before the @accepts and @returns decorators.
    _________________________________

    Usage:
    Put the decorator before the function like:
    @accepts(class1, class2, class3)
    def function(x, y, z)

    The "self" parameter and "class" parameter(in class methods) must be not indicated.

    One of three degrees of enforcement may be specified by passing
    the 'debug' keyword argument to the decorator:
        0 -- NONE:   No type-checking. Decorators disabled.
        1 -- MEDIUM: Print warning message to stderr. (Default)
        2 -- STRONG: Raise TypeError with message.
    If 'debug' is not passed to the decorator, the default level is used.

    Example usage:
        >>> if(True):
        ...     NONE, MEDIUM, STRONG = 0, 1, 2
        ...     @Dec.accepts(int, int, int)
        ...     @Dec.returns(float)
        ...     def average(x, y, z):
        ...         return (x + y + z) / 2
        ...     sys.stderr= sys.stdout #Doctest purpose only
        ...     average(5.5, 10, 15.0)
        ...
        TypeWarning:  'average' method accepts (int, int, int), but was given (float, int, float)
        15.25
        >>> average(5, 10, 15)
        TypeWarning:  'average' method returns (float), but result is (int)
        15

        In fibonaci, the param must be a integer, so if it is not a integer, it'll raise an error,
        not a warning. Indicated that with the debug=3 param.
        >>> if(True):
        ...     @Dec.accepts(int, debug=STRONG)
        ...     @Dec.returns(int, debug=STRONG)
        ...     def fib(n):
        ...         if n in (0, 1): return n
        ...         return fib(n-1) + fib(n-2)
        ...
        ...     fib(5.3)
        Traceback (most recent call last):
          ...
        TypeError: 'fib' method accepts (int), but was given (float)
    '''
    @staticmethod
    def info(fname, expected, actual, flag):
        '''  Convenience function returns nicely formatted error/warning messages. '''
        format = lambda types: ', '.join([str(t) for t in types])
        expected, actual = format(expected), format(actual)
        msg = "'%s' method " % fname \
              + ("accepts", "returns")[flag] + " (%s), but " % expected\
              + ("was given", "result is")[flag] + " (%s)" % actual
        return msg

    @staticmethod
    def accepts(*types, **kw):
        '''
        Function decorator. Checks that inputs given to decorated function
        are of the expected type.

        Parameters:
        @param types:
        The expected types of the inputs to the decorated function.
        Must specify type for each parameter.

        @param kw:
        Optional specification of 'debug' level (this is the only valid
        keyword argument, no other should be given).
        debug = ( 0 | 1 | 2 )

        '''
        if not kw:
            # default level: MEDIUM
            debug = 1
        else:
            debug = kw['debug']
        try:
            def decorator(f):
                def newf(*args):
                    if debug == 0:
                        return f(*args)
                    #if class param exists, look for if the param is a class, if it is, acces
                    #to the name of the class like a normal param
                    argtypes = []
                    for i in args:
                        if(type(i).__name__ != 'classobj'):
                            ap = i.__class__.__name__
                        else:
                            ap = i.__name__
                        argtypes.append(ap)
                    modTypes = [i.__name__ for i in types]

                    #if self param exists...look for this functions in the class of the object
                    #Lookely, if the function is static, the function doesn't show in globals of
                    #the class
                    if(f.__name__ in dir(f.func_globals[argtypes[0]])):
                        del argtypes[0]
                    assert len(argtypes) == len(modTypes)
                    if argtypes != modTypes:
                        msg = Dec.info(f.__name__, modTypes, argtypes, 0)
                        if debug == 1:
                            print >> sys.stderr, 'TypeWarning: ', msg
                        elif debug == 2:
                            raise TypeError, msg
                    return f(*args)
                newf.__name__ = f.__name__
                return newf
            return decorator
        except KeyError, key:
            raise KeyError, key + "is not a valid keyword argument"
        except TypeError, msg:
            raise TypeError, msg

    @staticmethod
    def returns(*ret_types, **kw):
        '''
        Function decorator. Checks that inputs given to decorated function
        are of the expected type.

        Parameters:
        @param ret_types:
        The expected types of returns of the decorated function.
        Must specify type for each parameter.

        @param kw:
        Optional specification of 'debug' level (this is the only valid
        keyword argument, no other should be given).
        debug = ( 0 | 1 | 2 )

        '''
        if not kw:
            # default level: MEDIUM
            debug = 1
        else:
            debug = kw['debug']
        try:
            def decorator(f):
                def newf(*args):
                    if debug == 0:
                        return f(*args)
                    result = f(*args)
                    if(result.__class__.__name__ != 'tuple'):
                        lista = []
                        lista.append(result)
                        result = lista
                    else:
                        result = list(result)
                    modTypes = [i.__name__ for i in ret_types]
                    if(len(result) > 1):
                        restypes = [i.__class__.__name__ for i in result]
                    else:
                        restypes = [result[0].__class__.__name__]
                    assert len(modTypes) == len(result)
                    print restypes
                    print modTypes
                    if restypes != modTypes:
                        msg = Dec.info(f.__name__, modTypes, restypes, 1)
                        if debug == 1:
                            print >> sys.stderr, 'TypeWarning: ', msg
                        elif debug == 2:
                            raise TypeError, msg
                    return f(*args)
                newf.__name__ = f.__name__
                return newf
            return decorator
        except KeyError, key:
            raise KeyError, key + "is not a valid keyword argument"
        except TypeError, msg:
            raise TypeError, msg

    '''
    Do a profile of a function
    @warning: (Not implemented yet)
    '''
    @staticmethod
    def trace(f):
        def globaltrace(frame, why, arg):
            if why == "call":
                return localtrace
            return None

        def localtrace(frame, why, arg):
            if why == "line":
                # record the file name and line number of every trace
                filename = frame.f_code.co_filename
                lineno = frame.f_lineno

                bname = os.path.basename(filename)
                print "%s(%d): %s" % (bname, lineno,
                                      linecache.getline(filename, lineno)),
            return localtrace

        def _f(*args, **kwds):
            sys.settrace(globaltrace)
            result = f(*args, **kwds)
            sys.settrace(None)
            return result

        return _f

if __name__ == "__main__":
    import doctest
    doctest.testmod()
