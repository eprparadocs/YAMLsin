from enum import Enum

class KeyType(Enum):
    REQUIRED = 0,
    OPTIONAL = 1


def isInAll(dicta, key):
    for k in dicta:
        if key not in dicta[k]:
            return(False)
    return(True)

def generateType(value) -> str:
    if isinstance(value, bool):
        return("bool")
    elif isinstance(value, int):
        return("int")
    elif isinstance(value, float):
        return("float")
    elif isinstance(value, dict):
        return("dict")
    elif isinstance(value, list):
        return("list")
    elif isinstance(value, tuple):
        return("tuple")
    elif isinstance(value, str):
        return("str")
    else:
        return("None")


def AnalyzeDict(instr: dict, lvl: str, bSingle: bool = True) -> dict:
    """
    This function is meant to analyze a dictionary, and its subdictionaries
    if bSingle is False.  We return information about symbols. When we are
    analyzing subdictionaries we expect all of them to have a common data
    type for a name common to all the subdictionaries.
    """

    def sameDataType(dicta, key):
        commonType = None
        values = []
        if key not in dicta:
            for k in dicta:
                if key in dicta[k]:
                    val = dicta[k][key]
                    commonType = generateType(val) if not commonType else commonType
                    if commonType != generateType(val):
                        raise ValueError(f"key {key} in dictionary doesn't have a common data type.")
                    if commonType in ['bool', 'int', 'float', 'None', 'str']:
                        if val not in values:
                            values.append(val)
                    elif commonType in ['dict']:
                        values = [val]
                    else:
                        pass
        else:
            val = dicta[key]
            commonType = generateType(val)
            values = [val]
        return(commonType, values)

    # Collect the keys from all the subdictionaries in
    # the main dictionary.'bSingle' if true, means that
    # we aren't to do subdictionaries, just the one we
    # are looking= at. If it is false, we will also look
    # at the subdictionaries of the main one.
    key_set = set()
    for key in instr.keys():
        if not bSingle and isinstance(instr[key], dict):
            key_set = key_set | set(instr[key].keys())
        else:
            key_set = key_set | set([key])

    # We need to make certain each key in the key_set has a
    # common data type. If not, we have an issue we can't
    # consolidate the data.
    #
    #TODO: while we expect same named keys to have the same
    # data type even in different subdictionaries, right now
    # we just annouce a Value error! We have no way to handle
    # names in common, in different subdirectories that have
    # different data types.
    dtype_dict = {}
    for key in key_set:
        if (dtype := sameDataType(instr, key)):
            dname = 'DICT_TOP' if dtype[0] == 'dict' else 'LIST'
            dname = dname + lvl[1:].upper().replace('.', '_') + '_' + key.upper().replace(" ", "").replace('(', '_').replace(')', '_')
            dtype_dict[key] = {'dtype': dtype[0],
                               'level': f"{lvl}.{key}" if dtype[0] == 'dict' else lvl,
                               'range': [dname, dtype[1]] if dtype[0] in ['dict','list','set','tuple'] else dtype[1],
                                }
        else:
            raise ValueError('Different data types for same named keys.')

    # For each of the keys in key_set, see if it is in
    # every dictionary or only in some. It is is in all
    # subdictionaries, the variable is required. Otherwise
    # it is optional.
    for key in key_set:
        if bSingle or isInAll(instr, key):
            dtype_dict[key]['keytype'] = KeyType.REQUIRED
        else:
            dtype_dict[key]['keytype'] = KeyType.OPTIONAL

    return(dtype_dict)
