
"""Yes I know it's not Pythonic to type check, but for pylinac, I don't see many alternatives. Note that these are for Classes."""
from __future__ import print_function, division, absolute_import
from builtins import zip
from builtins import str

try:
    from __builtin__ import unicode
except:
    pass
from future import standard_library
standard_library.install_aliases()

# The following is adapted from: http://code.activestate.com/recipes/578809-decorator-to-check-method-param-types/
# Another type checking decorator: http://code.activestate.com/recipes/454322-type-checking-decorator/
from functools import wraps


def property_check(**props):
    """Decorator to check that the given properties exist and/or have a given value."""


def type_accept(**types):
    """Function decorator enforcing input types. This wouldn't be needed for a Py3-only project where function annotation is allowed.
    But for 2.7 compatibility, this decorator is a replacement of sorts.

    :param types: expected types (e.g. str, int, float).
    """
    def type_decor(func):  # func == function to decorate
        @wraps(func)
        def new_func(*args, **kwargs):  # the decorated function's arguments'
            # if self is first argument, i.e. a class method, remove it. Otherwise the arg values and arg names are not the same length.
            if func.__code__.co_varnames[0] == 'self':
                arg_names = func.__code__.co_varnames[1:]
                arg_vals = args[1:]
            else:
                arg_names = func.__code__.co_varnames
                arg_vals = args
            # check positional arguments
            for arg_name, arg_val in zip(arg_names, arg_vals):
                if arg_name in types:
                    if not isinstance(arg_val, types[arg_name]):
                        raise TypeError("Argument '{}' was not of type {}".format(arg_val, str(types[arg_name]).split("'")[1]))
            # check keyword arguments
            for arg_name, arg_val in kwargs.items():
                if arg_name in types:
                    if not isinstance(arg_val, types[arg_name]):
                        raise TypeError("Argument '{}' was not of type {}".format(arg_val, str(types[arg_name]).split("'")[1]))
            return func(*args, **kwargs)
        new_func = unwrap_func(new_func)
        return new_func
    return type_decor

def value_accept(**val_accept):
    """Function decorator enforcing input values.

    :param val_accept: expected values. These can be in (lower, upper) for int or float, and in ('str1', 'str2') for string matching. E.g.
    (1, 10) means accept a value between 1 and 10. ('str1', 'str2') means the value must be one of the listed strings.
    """
    def decorator(func):  # func == function to decorate
        @wraps(func)
        def new_func(*args, **kwargs):  # the decorated function's arguments'
            # func = unwrap_func(func)
            # check positional arguments
            # if self is first argument, i.e. a class method, remove it. Otherwise the arg values and arg names are not the same length.
            # func = unwrap_func(func)
            # www = func.__code__.co_varnames
            if func.__code__.co_varnames[0] == 'self':
                arg_names = func.__code__.co_varnames[1:]
                arg_vals = args[1:]
            else:
                arg_names = func.__code__.co_varnames
                arg_vals = args
            for arg_name, arg_val in zip(arg_names, arg_vals):
                if arg_name in val_accept:
                    if type(arg_val) in (float, int):
                        if not val_accept[arg_name][0] <= arg_val <= val_accept[arg_name][1]:
                            raise ValueError("Argument '{}' needs to be between {:f} and {:f}".format(arg_name, val_accept[arg_name][
                                0], val_accept[arg_name][1]))
                    elif type(arg_val) in (str,) or type(arg_val.decode()) in (unicode,):
                        if not arg_val in val_accept[arg_name]:
                            raise ValueError("Argument '{}' passed to '{}' needs to be one of these: {}".format(arg_name, func.__name__,
                                                                                                                    val_accept[arg_name]))
            # check keyword arguments
            for arg_name, arg_val in kwargs.items():
                if arg_name in val_accept:
                    if type(val_accept[arg_name][0]) in (float, int):
                        if not val_accept[arg_name][0] <= arg_val <= val_accept[arg_name][1]:
                            raise ValueError("Argument '{:f}' passed to '{}' needs to be between {:f} and {:f}".format(arg_name,
                                                                                                                      func.__name__,
                                                                                                           val_accept[arg_name][0],
                                                                                                        val_accept[
                                                                                                            arg_name][1]))
                    elif type(val_accept[arg_name][0]) in (str,):
                        if not arg_val in val_accept[arg_name]:
                            raise ValueError("Argument '{}' passed to '{}' needs to be one of these: {}".format(arg_name, func.__name__,
                                                                                                             val_accept[arg_name]))
            return func(*args, **kwargs)
        func = unwrap_func(new_func)
        return new_func
    return decorator


def unwrap_func(wrapped_func, unwraps=0):
    """Return an unwrapped function from the wrapped function.

    Functions or methods can use one or more decorators. If the decorator needs access to the base function (e.g. its arguments), it
    won't get it if more than 1 decorator is used. This function allows one to get to the base function, or a function wrapped a certain
    number of times. The function must be wrapped with the stdlib functools.wraps for proper unwrapping.

    Discussion of this issue: http://bugs.python.org/issue17482

    :param unwraps: The number of times to unwrap a function, if wrapped with multiple decorators. If 0 or negative, will return the base
        function.
    :type unwraps: int
    """
    func = wrapped_func
    # if we want the base function
    if unwraps <= 0:
        at_base = False
        while not at_base:
            try:
                func = func.__wrapped__
            except AttributeError:
                at_base = True

    # else we want the function unwrapped n times
    else:
        for unwrap in range(unwraps):
            try:
                func = func.__wrapped__
            except AttributeError:
                break

    return func