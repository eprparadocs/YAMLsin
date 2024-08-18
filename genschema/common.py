""" common - common functions used by the validator

    generateType - takes a data type and returns a class name.

"""

# Common functions
def generateType(d):
    """
    Return name of data type.

    Args:
        d       Data to examine for type

    Returns:
        Type of data

    Raises:
        None
    """
    cooltypes = {
        type([]): "list",
        type({}): "dict",
        type(()): "tuple",
        type(1): "int",
        type(1.0): "float",
        type(True): "bool",
        type("c"): "char",
    }
    return cooltypes[type(d)]
