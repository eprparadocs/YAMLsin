import yaml
from enum import Enum

from analyze import AnalyzeDict


# Describe what type of output file we are dealing with - real or buffered writer.
class TypeOfFile(Enum):
    REAL = 0
    BUFFERED = 1

class KeyType(Enum):
    REQUIRED = 0,
    OPTIONAL = 1


class OUTPUT:
    def __init__(self, ofilename = None) -> None:
        if ofilename:
            self.fd = open(ofilename, 'w')
            self.buff = None
        else:
            self.fd = None
            self.buff = ''

    def write(self, buf) -> None:
        if self.fd:
            self.fd.write(buf)
        else:
            self.buff = self.buff + buf

    def flush(self) -> None:
        if self.fd:
            self.fd.flush()

    def close(self) -> None:
        if self.fd:
            self.fd.close()


class Stack:
    def __init__(self):
        self.stack = []

    def Push(self, data):
        self.stack.append(data)

    def Pop(self):
        return self.stack.pop()

    def more(self):
        return len(self.stack)


def genType(v):
    if isinstance(v, bool):
        return 'bool'
    elif isinstance(v, int):
        return 'int'
    elif  isinstance(v, float):
        return 'float'
    elif isinstance(v, dict):
        return 'dict'
    elif isinstance(v, list):
        return 'list'
    elif isinstance(v, tuple):
        return 'tuple'
    elif isinstance(v, set):
        return 'set'
    elif isinstance(v, str):
        return 'str'
    elif isinstance(v, None):
        return 'None'
    raise TypeError


def CollectSymbols(yaml: str, level: str or None, symtable: dict = None, dictable: dict = None) -> dict:
    """
    We make a pass over the YAML to figure information about each of the keys
    in the YAML and the options that they take on.
    """
    for key, value in yaml.items():
        ktype = genType(value)
        if ktype == 'dict':
            if key in dictable:
                if level not in dictable[key]:
                    # Same symbol name, different level. So we have a different symbol!
                    # We record the level and tyep of data.
                    dictable[key][level] = ktype
            else:
                # We have a new symbol, so add it.
                dictable[key] = {}
                dictable[key][level] = ktype
            CollectSymbols(value, f"{level}.{key}", symtable, dictable)
        else:
            if key in symtable:
                if level not in symtable[key]:
                    # Same symbol name, different level. So we have a different symbol!
                    # We record the level and tyep of data.
                    symtable[key][level] = ktype
            else:
                # We have a new symbol, so add it.
                symtable[key] = {}
                symtable[key][level] = ktype


def GenerateSynmbolNames(symtable: dict, outfd) -> None:
    """
    To make it easy to change the symbols used in the YAML file
    we define some equivalents here.
    """
    for key in symtable:
        outfd.write(f'sym_{key.upper().replace(" ", "").replace('(', '_').replace(')', '_')} = "{key}"\n')


def generateItem(outfd, key, lvl: str, gensym: bool, dtype, ktype) -> None:
    fname = "top_" + lvl.replace('.', "_") + "_" + key
    if gensym:
        symkey =  f"[sym_{key.upper().replace(' ', '').replace('(', '_').replace(')', '_')}"
    else:
        symkey =  "[" + "'" + key.upper().replace(' ', '').replace('(', '_').replace(')', '_') + "'"
    chkname = f"check_{fname.upper().replace(' ', '').replace('(', '_').replace(')', '_').replace('.', '_')}"
    if not dtype:
        dtype = 'str'
    if dtype == 'bool':
        outfd.write(f"{symkey},{chkname},bool,{ktype}],\n")
    elif dtype == 'int':
        outfd.write(f"{symkey},{chkname},int,{ktype}],\n")
    elif dtype == 'float':
        outfd.write(f"{symkey},{chkname},float,{ktype}],\n")
    elif dtype == 'dict':
        dname = 'DICT_TOP' + lvl[1:].upper().replace('.', '_') + '_' + key.upper().replace(" ", "").replace('(', '_').replace(')', '_')
        outfd.write(f"{symkey},'chkDict','{dname}',{ktype}],\n")
    elif dtype == 'list':
        dname = 'LIST' + lvl[1:].upper().replace('.', '_') + '_' + key.upper().replace(" ", "").replace('(', '_').replace(')', '_')
        outfd.write(f"{symkey},'chkList','{dname}',{ktype}],\n")
    elif dtype == 'tuple':
        outfd.write(f"{symkey},{chkname},set,{ktype}],\n")
    elif dtype == 'str':
        outfd.write(f"{symkey},{chkname},str,{ktype}],\n")


def generateAggItem(outfd, key, lvl: str, gensym: bool, dtype, ktype, rangeOfValues) -> None:
    if gensym:
        symkey =  f"[sym_{key.upper().replace(' ', '').replace('(', '_').replace(')', '_')}"
    else:
        symkey =  "[" + "'" + key.upper().replace(' ', '').replace('(', '_').replace(')', '_') + "'"
    if not dtype:
        dtype = 'str'
    if dtype == 'bool':
        outfd.write(f"{symkey},'chkBoolRange',{rangeOfValues},{ktype}],\n")
    elif dtype == 'int':
        outfd.write(f"{symkey},'chkIntRange',{rangeOfValues},{ktype}],\n")
    elif dtype == 'float':
        outfd.write(f"{symkey},'chkFloatRange',{rangeOfValues},{ktype}],\n")
    elif dtype == 'dict':
        dname = 'DICT_TOP' + lvl[1:].upper().replace('.', '_') + '_' + key.upper().replace(" ", "").replace('(', '_').replace(')', '_')
        outfd.write(f"{symkey},'chkDict','{dname}',{ktype}],\n")
    elif dtype == 'list':
        outfd.write(f"{symkey},'chkListRange',{rangeOfValues},{ktype}],\n")
    elif dtype == 'tuple':
        outfd.write(f"{symkey},'chkSetRange',{rangeOfValues},{ktype}],\n")
    elif dtype == 'str':
        outfd.write(f"{symkey},'chkStrRange',{rangeOfValues},{ktype}],\n")


def genSub(outfd, k: str, dtype: str, level: str, RoV: str = None):
    """
    	if isinstance(item, str):
		if item in {RoV}:
			return True, None
		else:
			return False,  [["E", 1001, f"Expected {RoV} and got {item}  at {level}."]]
	else:
		return False, [["E", 1000, f"Didn't get expected str for '{item}' at {level}."]]
    """
    outfd.write('\n')
    fname = "top_" + level.replace('.', "_") + "_" + k
    outfd.write(f"def check_{fname.upper().replace(' ', '').replace('(', '_').replace(')', '_').replace('.', '_')}(item, lvl, datatype, _):\n")
    outfd.write(f"\tif isinstance(item, {dtype}):\n"),
    if RoV:
        outfd.write(f"\t\tif item in {RoV}:\n")
    else:
        outfd.write(f"\t\t FILL IN YOUR TEST")
    outfd.write(f"\t\t\treturn True,None\n")
    outfd.write(f"\t\telse:\n")
    a = [str(x) for x in RoV]
    RoVString = ','.join(a)
    s =  f'f\"Expected \'{RoVString}\' and got {{item}} at {{lvl}} instead.\"'
    outfd.write("\t\t\treturn False, [['E',1000, "+s+"]]\n")
    outfd.write(f"\telse:\n")
    outfd.write(f"\t\treturn False, [['E', 1001, 'BAR']]\n\n")


def YamlScanner(infile: str|None = None, outfd=None, analyze: list|None = None,
                generate: bool = False) -> bool | tuple[bool, str]:
    """
    This function will process the input and outfiles and scan the YAML input.
    If the outfile is None, the function will return both an boolean and string.
    The bool will be True if the YAML file is valid and has been scanned succesfully.
    The string will be the output produced by the scanner (if bool is True). If the
    bool is False it means the scanner failed because the YAML wasn't valid.

    If we have a real output file, the output of the scanner is written to the file,
    and the return is a bool. If the bool is True, the output file contains the result
    of the scanning. If it is False it will contain information about the reason the
    scan failed.
    """

    def AnalyzeList(instr: dict, lvl: str) -> dict:
        # Analyze the list, and set it up
        dicts = {}
        scalars = []
        incr = 0
        for i in instr:
            if isinstance(i, (str, float, int, bool)):
                scalars.append(i)
            elif isinstance(i, (list, tuple, set)):
                pass
            else:
                dlvl = f"DICT_LIST_ITEM_{lvl[1:]}_{incr}"
                incr += 1
                stack.Push([dlvl, i, lvl, False])
                dicts[dlvl] = i
        return [scalars, dicts]

    # Setup the analyze list, just in case. These are dictionary entries
    # that are really like lists of named entries. We will create a single
    # entry that will handle all the variations.
    dict_list = []
    if analyze:
        for a in analyze:
            dname = 'DICT_TOP_' + a.upper().replace('.', '_')
            dict_list.append(dname)

    # Dictionary stack
    stack = Stack()

    # Open the input file and process it.
    with open(infile) as stream:
        try:
            # Get the file contents
            data = yaml.safe_load(stream)

            # Collect information about the YAML file. We need all the
            # keys used in the YAML file. We generate some equivalencies
            # for the keys (to make it easier to change key names without
            # generating a new YAML layout.)
            SymTable = {}
            DictTable = {}
            CollectSymbols(data, '.', SymTable, DictTable)

            # Are we going to generate chk subrouines
            outfd.write("from enum import Enum\n\n")
            outfd.write("class KeyType(Enum):\n\tREQUIRED = 0,\n\tOPTIONAL = 1\n\n")
            if generate:
                GenerateSynmbolNames(SymTable, outfd)
                GenerateSynmbolNames(DictTable, outfd)
                outfd.write('\n\n\n')
                outfd.flush()

            # Push on the top dictionary entry.
            stack.Push(["DICT_TOP",data, '.', True])

            # Process the YAMP one dictionary at a time.
            while stack.more():
                name, data, lvl, gensym = stack.Pop()
                dtype = 'dict' if name.startswith('DICT') else 'list'
                if dtype == 'dict':
                    aFlag = name not in dict_list
                    rc = AnalyzeDict(data, lvl, aFlag)

                    # First pass through the return data - generate any necessary check
                    # subroutines
                    if generate:
                        for item, value in rc.items():
                            dtype = value['dtype']
                            if dtype not in ['dict', 'list', 'tuple', 'set']:
                                RoV = value['range']
                                genSub(outfd, item, dtype, lvl, RoV, )

                    # We handle the processing differently for aggregated entries
                    # and individual ones.
                    outfd.write(f"{name} = [\n")
                    if aFlag:
                        # Individual really
                        for item, value in rc.items():
                            dtype = value['dtype']
                            ktype = value['keytype']
                            if dtype == 'dict':
                                generateItem(outfd, item, lvl, gensym, dtype, ktype)
                                stack.Push([value['range'][0], value['range'][1][0], value['level'], gensym])
                            elif dtype in ['list', 'tuple', 'set']:
                                generateItem(outfd, item, lvl, gensym, dtype, ktype)
                                stack.Push([value['range'][0], value['range'][1][0], value['level'], gensym])
                            else:
                                # Scalar type
                                generateItem(outfd, item, lvl, gensym, dtype, ktype)
                    else:
                        # Aggregated entry.
                        for item, value in rc.items():
                            dtype = value['dtype']
                            ktype = value['keytype']
                            rangeOfValues = value['range']
                            generateAggItem(outfd, item, lvl, gensym, dtype, ktype, rangeOfValues)
                    outfd.write(']\n\n')
                else:
                    # Analyze the list, tuple, set
                    scalars, dicts = AnalyzeList(data, lvl)

                    # Define the list entity
                    outfd.write(f"{name} = [\n")

                    # Write out the scalar and dicts list
                    outfd.write("['level','"+lvl+'.'+name+"'],\n")
                    outfd.write("['scalars', "+str(scalars)+"],\n")
                    outfd.write("['dictionaries', "+str(dicts)+"],\n")
                    outfd.write(']\n\n')
                outfd.flush()

        except yaml.YAMLError as exc:
            print(exc)




if __name__ == '__main__':
    from argparse import ArgumentParser
    from os.path import isfile

    # Parse the command line arguments
    parser = ArgumentParser(
        prog='YAMLScanner',
        description='Program to scan a YAML file and create prototype.'
    )
    parser.add_argument('-o', '--output', default=None, help="Where to write JSON data.")
    parser.add_argument('-a', '--analyze', default=None, action='append', help='What YAML dictionaries can be analyzed.')
    parser.add_argument('-g', '--generate', type=bool, default=False, help='Generate code.')
    parser.add_argument('input', help='YAML input file')
    args = parser.parse_args()

    # Validate the input filename, making certain it is a text file and
    # readable.
    if not isfile(args.input):
        print(f"File {args.input} either doesn't exist or isn't a file.")
        exit(1)

    # Figure out what we are doing with the output side. If there is no
    # output file, we will create a fake buffered write file. If we have a
    # real file, open it up for writing.
    if args.output:
        # We have a real file, open it up for writing.
        filetype = TypeOfFile.REAL
        outfd = OUTPUT(args.output)
    else:
        # Ceate a buffered writer to collect the output.
        filetype = TypeOfFile.BUFFERED
        outfd = OUTPUT(None)

    # Call the scanner.
    rc = YamlScanner(args.input, outfd, args.analyze, args.generate)

    # If we have a buffered file, we will need to convert it to a
    # string and return it.
    if filetype == TypeOfFile.REAL:
        # Close the real file
        outfd.close()
    else:
        # Get a string with the contents.
        ostr = outfd.buff
        print(ostr)


