from antlr4 import *
from JSONLexer import JSONLexer as Lexer
from JSONListener import JSONListener as Listener
from JSONParser import JSONParser as JSONParser
import sys

InArrayFlag = False
LevelName = None

__VERSION__ = '0.1'

class JSONPrintListener(Listener):

    def __init__(self, fileName):
        Listener.__init__(self)
        self.filename = fileName
        self.fptr = open(fileName,'w')

    def enterJson(self, ctx:JSONParser.JsonContext):
        global LevelName
        LevelName = 'TOP'

    # Exit a parse tree produced by JSONParser#json.
    def exitJson(self, ctx:JSONParser.JsonContext):
        self.fptr.flush()
        self.fptr.close()
        self.fptr = None


    # Enter a parse tree produced by JSONParser#AnObject.
    def enterAnObject(self, ctx:JSONParser.AnObjectContext):
        print('[', file=self.fptr)

    # Exit a parse tree produced by JSONParser#AnObject.
    def exitAnObject(self, ctx:JSONParser.AnObjectContext):
        print( '],', file=self.fptr)


    # Enter a parse tree produced by JSONParser#EmptyObject.
    def enterEmptyObject(self, ctx:JSONParser.EmptyObjectContext):
        pass

    # Exit a parse tree produced by JSONParser#EmptyObject.
    def exitEmptyObject(self, ctx:JSONParser.EmptyObjectContext):
        pass


    # Enter a parse tree produced by JSONParser#ArrayOfValues.
    def enterArrayOfValues(self, ctx:JSONParser.ArrayOfValuesContext):
        global InArrayFlag
        InArrayFlag = True
        print('[', end=' ', file=self.fptr)

    # Exit a parse tree produced by JSONParser#ArrayOfValues.
    def exitArrayOfValues(self, ctx:JSONParser.ArrayOfValuesContext):
        global InArrayFlag
        InArrayFlag = False
        print('],', file=self.fptr)

    # Enter a parse tree produced by JSONParser#EmptyArray.
    def enterEmptyArray(self, ctx:JSONParser.EmptyArrayContext):
        print("[],", file=self.fptr)

    # Exit a parse tree produced by JSONParser#EmptyArray.
    def exitEmptyArray(self, ctx:JSONParser.EmptyArrayContext):
        pass


    # Enter a parse tree produced by JSONParser#pair.
    def enterPair(self, ctx:JSONParser.PairContext):
        s = ctx.STRING().getText()
        global LevelName
        LevelName = LevelName + '.' + s[1:-1]
        print( '["' + LevelName + '",', end='', file=self.fptr)

    # Exit a parse tree produced by JSONParser#pair.
    def exitPair(self, ctx:JSONParser.PairContext):
        print('],', file=self.fptr)
        global LevelName
        LevelName, post = LevelName.rsplit('.', 1)



    # Enter a parse tree produced by JSONParser#String.
    def enterString(self, ctx:JSONParser.StringContext):
        global InArrayFlag
        end = ' ' if InArrayFlag else '\n'
        print(ctx.getText() + ', ', end=end, file=self.fptr)

    # Exit a parse tree produced by JSONParser#String.
    def exitString(self, ctx:JSONParser.StringContext):
        pass


    # Enter a parse tree produced by JSONParser#Atom.
    def enterAtom(self, ctx:JSONParser.AtomContext):
        s = ctx.getText()
        if s == 'true':
            s = 'True'
        elif s == 'false':
            s = 'False'
        elif s == 'null':
            s = 'None'
        print(s + ', ', file=self.fptr)

    # Exit a parse tree produced by JSONParser#Atom.
    def exitAtom(self, ctx:JSONParser.AtomContext):
        pass


    # Enter a parse tree produced by JSONParser#ObjectValue.
    def enterObjectValue(self, ctx:JSONParser.ObjectValueContext):
        pass

    # Exit a parse tree produced by JSONParser#ObjectValue.
    def exitObjectValue(self, ctx:JSONParser.ObjectValueContext):
        pass


    # Enter a parse tree produced by JSONParser#ArrayValue.
    def enterArrayValue(self, ctx:JSONParser.ArrayValueContext):
        pass

    # Exit a parse tree produced by JSONParser#ArrayValue.
    def exitArrayValue(self, ctx:JSONParser.ArrayValueContext):
        pass


def main():
    from argparse import ArgumentParser
    from os.path import isdir, basename, join
    from os import remove, chdir
    from pprint import pprint
    parser = ArgumentParser(prog='YAML compile', description='Read YAML script and compile down requirements.')
    parser.add_argument('-o', '--outdir', default='.', action='store', help="Where to write the output.")
    parser.add_argument('-p', '--print', default=False, action='store_true', help="Create Pretty Print output.")
    parser.add_argument('-v', '--version', default=False, action='store_true', help="Print version on stdout and exit.")
    parser.add_argument('input', nargs='*')
    args = parser.parse_args()

    # See if we are just going to output the version and exit.
    if args.version:
        print(f"YAMLcompile Version  {__VERSION__}")
        sys.exit(0)

    # Make certain the outdir is really present and a directory.
    if not isdir(args.outdir):
        print(f"Error: {args.outdir} is not a directory", file=sys.stderr)
        sys.exit(1)


    # Process the input, one file at a time.
    for f in args.input:
        input_stream = FileStream(f)
        #  input_stream = StdinStream()
        #  input_stream = InputStream(<string>)
        lexer = Lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = JSONParser(stream)
        tree = parser.json()
        outfile = join(args.outdir, basename(f).split('.')[0] + '.tmp')
        printer = JSONPrintListener(outfile)
        walker = ParseTreeWalker()
        walker.walk(printer, tree)

        # Pretty print the output file
        if args.print:
            with open(outfile, 'r') as infile:
                content = eval('[' + infile.read().rstrip(',\n') + ']')
                ppoutfile = join(args.outdir, basename(f).split('.')[0] + '.txt')
                with open(ppoutfile, 'w') as fp:
                    pprint(content, stream=fp, indent=4, width=120)
            remove(outfile)


if __name__ == '__main__':
    main()