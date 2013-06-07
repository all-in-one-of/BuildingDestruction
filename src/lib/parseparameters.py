
def parse_parameters(parameters, default_parameters):
    '''
    Given a dictionary of default parameters, parse a custom dictionary of
    parameters, being a subgroup of all default parameters, add the faulting
    parameters with default values to the user custom dictionary of parameters.
    
    i.e.
    >>> parameters = {'value_1': 2, 'value_3': 5}
    >>> default_parameters = {'value_1': 1, 'value_2': 2, 'value_3': 3, 'value_4': 4}
    >>> parsed_parameters = parse_parameters(parameters, default_parameters)
    >>> sorted(parsed_parameters.items(), key = lambda parameter: parameter[0])
    [('value_1', 2), ('value_2', 2), ('value_3', 5), ('value_4', 4)]
    '''
    parsed_parameters = {}
    for key in default_parameters.keys():
        if(key in parameters.keys()):
            parsed_parameters[key] = parameters[key]
        else:
            parsed_parameters[key] = default_parameters[key]
    return parsed_parameters

def test():
    import doctest
    from lib import parseparameters
    doctest.testmod(parseparameters, verbose = True)
    
if __name__ == "__main__":
    test()