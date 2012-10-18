# -*- coding: utf-8 -*-
import sys
import functools
class TypeEnforcement:
    """
    One of three degrees of enforcement may be specified by passing
    the 'debug' keyword argument to the decorator:
        0 -- NONE:   No type-checking. Decorators disabled.
        1 -- MEDIUM: Print warning message to stderr. (Default)
        2 -- STRONG: Raise TypeError with message.
    If 'debug' is not passed to the decorator, the default level is used.

    Example usage:
        >>> NONE, MEDIUM, STRONG = 0, 1, 2
        >>>
        >>> @accepts(int, int, int)
        ... @returns(float)
        ... def average(x, y, z):
        ...     return (x + y + z) / 2
        ...
        >>> average(5.5, 10, 15.0)
        TypeWarning:  'average' method accepts (int, int, int), but was given
        (float, int, float)
        15.25
        >>> average(5, 10, 15)
        TypeWarning:  'average' method returns (float), but result is (int)
        15

    Needed to cast params as floats in function def (or simply divide by 2.0).

        >>> TYPE_CHECK = STRONG
        >>> @accepts(int, debug=TYPE_CHECK)
        ... @returns(int, debug=TYPE_CHECK)
        ... def fib(n):
        ...     if n in (0, 1): return n
        ...     return fib(n-1) + fib(n-2)
        ...
        >>> fib(5.3)
        Traceback (most recent call last):
          ...
        TypeError: 'fib' method accepts (int), but was given (float)

    """
    @staticmethod
    def accepts(*types, **kw):
        """ Function decorator. Checks that inputs given to decorated function
        are of the expected type.

        Parameters:
        types -- The expected types of the inputs to the decorated function.
                 Must specify type for each parameter.
        kw    -- Optional specification of 'debug' level (this is the only valid
                 keyword argument, no other should be given).
                 debug = ( 0 | 1 | 2 )

        """
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
                    assert len(args) == len(types)
                    argtypes = tuple(map(type, args))
                    if argtypes != types:
                        msg = TypeEnforcement.info(f.__name__, types, argtypes, 0)
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
    def returns(ret_type, **kw):
        """ Function decorator. Checks that return value of decorated function
        is of the expected type.

        Parameters:
        ret_type -- The expected type of the decorated function's return value.
                    Must specify type for each parameter.
        kw       -- Optional specification of 'debug' level (this is the only valid
                    keyword argument, no other should be given).
                    debug=(0 | 1 | 2)

        """
        try:
            if not kw:
                # default level: MEDIUM
                debug = 1
            else:
                debug = kw['debug']
            def decorator(f):
                def newf(*args):
                    result = f(*args)
                    if debug == 0:
                        return result
                    res_type = type(result)
                    if res_type != ret_type:
                        msg = TypeEnforcement.info(f.__name__, (ret_type,), (res_type,), 1)
                        if debug == 1:
                            print >> sys.stderr, 'TypeWarning: ', msg
                        elif debug == 2:
                            raise TypeError, msg
                    return result
                newf.__name__ = f.__name__
                return newf
            return decorator
        except KeyError, key:
            raise KeyError, key + "is not a valid keyword argument"
        except TypeError, msg:
            raise TypeError, msg
    @staticmethod
    def info(fname, expected, actual, flag):
        """ Convenience function returns nicely formatted error/warning msg. """
        format = lambda types: ', '.join([str(t).split("'")[1] for t in types])
        expected, actual = format(expected), format(actual)
        msg = "'%s' method " % fname \
              + ("accepts", "returns")[flag] + " (%s), but " % expected\
              + ("was given", "result is")[flag] + " (%s)" % actual
        return msg
    
class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)
