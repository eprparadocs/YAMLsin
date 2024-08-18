from types import ModuleType
from copy import deepcopy
import yaml

from common import generateType

_module = None


def chkDict(item: dict, nextdict: str, lvl: str, m: ModuleType) -> bool:
    # Make certain the item is really a dict.
    rc = isinstance(item, dict)
    errors = None
    if rc:
        # Try to find the list to check.
        if nextdict in m.__dict__:
            # It exists.
            errors = CycleThroughList(item, nextdict, lvl)
            rc = True if not errors else False
            return rc, errors
        else:
            # It doesn't exist.
            return False, [["E",5, f"Expected '{nextdict}' in '{lvl}' and not found."]]

    else:
        actualtype = generateType(item)
        return False, [["E",4, f"Expected dictionary data type for '{nextdict}' in '{lvl}' and got type '{actualtype}' instead"]]


def chkList(item: dict, nextdict: str, lvl: str, m: ModuleType) -> bool:
    rc = isinstance(item, list)
    errors = None
    if rc:
        # It exists, we will cycle through the list
        errors = CycleThroughList(item, nextdict, lvl)
        rc = True if not errors else False
        return rc, errors
    else:
        actualtype = generateType(item)
        return False, [["E",10, f"Expected list data type for '{nextdict}' in '{lvl}' and got type '{actualtype}' instead"]]



def chkStrRange(item: dict, nextdict: str, lvl: str, m: ModuleType) -> bool:
    rc = isinstance(item, str)
    if rc:
        return True, None
    else:
        return False,  ["E", 3, f"Wrong data type or value for '{key}'; {emsg}. "]

def chkBoolRange(item: dict, nextdict: str, lvl: str, m: ModuleType) -> bool:
    rc = isinstance(item, id)
    if rc:
        return True, None
    else:
        return False,  ["E", 3, f"Wrong data type or value for '{key}'; {emsg}. "]

def chkIntRange(item: dict, nextdict: str, lvl: str, m: ModuleType) -> bool:
    rc = isinstance(item, id)
    if rc:
        return True, None
    else:
        return False,  ["E", 3, f"Wrong data type or value for '{key}'; {emsg}. "]


toFunc = {'chkDict': chkDict, 'chkStrRange': chkStrRange,
          'chkIntRange': chkIntRange, 'chkBoolRange': chkBoolRange,
          'chkList': chkList,
          }
def ConvertFunction(func: str or callable) -> callable:
    if isinstance(func, str):
        func = toFunc[func]
    return func


def CycleThroughList(ydata: dict or list, listName:str, lvl: str, schemamod: str = None) -> []:
    """
    """

    # Find the actual list behind the listName from the scanner generated file.
    global _module
    if schemamod:
        _module = schemamod
    mod = schemamod if schemamod else _module

    #m =  globals().get(modName)
    l = mod.__dict__[listName]

    # We set this dynamically
    KeyType = mod.__dict__['KeyType']

    def DictCycle(ydata: dict, l: list, lvl: str) -> []:
        # Obvious check here - we better have a dictionary, otherwise we will never find anything!
        if not isinstance(ydata, dict):
            actualtype = generateType(ydata)
            return [["E",1, f"Expected dictionary data type for {listName} and got {actualtype} instead"]]

        errors = []
        loopdata = deepcopy(l)
        while loopdata:
            # We have an item, so see if it is present in the dictionary.
            #
            # For example each line is like this:
            #
            #            sym_TENANTNAME,check_TENANTNAME,str,'expected string value',KeyType.REQUIRED
            #
            key, chkfunc, datatype, opt = loopdata.pop()
            if key in ydata:
                # First make certain we have the correct type.
                chkfunc = ConvertFunction(chkfunc)
                rctemp, errs = chkfunc(ydata[key], datatype, f"{lvl}.{key}", mod)
                if not rctemp:
                    errors = errors + errs
                else:
                    # See if we have a special handler for this entry.
                    pass
            else:
                # It isn't present in the dictionary, so we will see if it is optional or not.
                if opt == KeyType.REQUIRED:
                    errors = errors + [["E", 2, f"Missing '{key}' for level '{lvl}'."]]
        return errors

    def ListCycle(ydata: list, l: list, lvl: str) -> []:
        # Obvious check here - we better have a dictionary, otherwise we will never find anything!
        if not isinstance(ydata, list):
            actualtype = generateType(ydata)
            return [["E",1, f"Expected list data type for {listName} and got {actualtype} instead"]]

        errors = []
        scalars, dicts, lists = [], [], []
        for i in l:
            if i[0] == 'scalars':
                scalars = i[1]
            if i[0] == 'dictionaries':
                dicts = i[1]
            if i[0] == 'list':
                lists = i[1]
            if i[0] == 'level':
                lvl = i[1]

        # Now we cycle through the data making sure everything is there.
        tempscalars = deepcopy(scalars)
        tempdicts = deepcopy(dicts)
        for item in ydata:
            if isinstance(item, (str, bool, int, float)):
                if item not in scalars:
                    errors = errors + [["E", 200, f"Extra item '{item}' for list at level '{lvl}'."]]
                else:
                    tempscalars.remove(item)
            elif isinstance(item, dict):
                # Test this dictionary against the definitions we have generated.
                found = False
                for key, d in dicts.items():
                    if not CycleThroughList(item, key, lvl):
                        found = True
                        break
                if not found:
                    errors = errors +  [["E", 200, f"Extra item '{item}' for list at level '{lvl}'."]]
                else:
                    tempdicts.pop(key)
            elif isinstance(item, (list, tuple, set)):
                lists

        # Anything left unfulfilled?
        for s in tempscalars:
            errors = errors + [["E", 201, f"Item '{s}' missing for list at level '{lvl}'"]]
        for d in tempdicts:
            errors = errors + [["E", 201, f"Item '{tempdicts[d]}' missing for list at level '{lvl}'"]]
        return errors


    # What type of item are we looking at?
    errors = DictCycle(ydata, l, lvl) if isinstance(ydata, dict) else ListCycle(ydata, l, lvl)

    # return whatever we have
    return errors


def YAMLCheck(schema: str, inputfile: str) -> []:

    # Load the schema file into our system.
    from importlib import __import__
    m = __import__(schema)

    ydfile = open(inputfile, 'r')
    ydata = yaml.safe_load(ydfile)
    ydfile.close()

    return CycleThroughList( ydata, "DICT_TOP", ".", schemamod = m)


if __name__ == '__main__':

        from argparse import ArgumentParser
        from os.path import isfile
        import pprint

        # Parse the command line arguments
        parser = ArgumentParser(
            prog='YAMLCheck',
            description='Program to check a YAML file.'
        )
        parser.add_argument('schema')
        parser.add_argument('input')
        args = parser.parse_args()

        # Validate the input filename, making certain it is a text file and
        # readable.
        if not isfile(args.input):
            print(f"File {args.input} either doesn't exist or isn't a file.")
            exit(1)
        if not isfile(args.schema+'.py'):
            print(f"File {args.schema} either doesn't exist or isn't a file.")
            exit(1)

        # Call the scanner.
        rc = YAMLCheck(args.schema, args.input)
        if rc:
            pprint.pprint(rc, width=120)
        else:
            print('Ok')

