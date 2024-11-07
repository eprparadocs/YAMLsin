from antlr4 import *
from JSONLexer import JSONLexer as Lexer
from JSONListener import JSONListener as Listener
from JSONParser import JSONParser as JSONParser
import sys

DictionaryLevel = None
InArrayFlag = False

class JSONPrintListener(Listener):

    def enterJson(self, ctx:JSONParser.JsonContext):
        global DictionaryLevel
        DictionaryLevel = 0

    # Exit a parse tree produced by JSONParser#json.
    def exitJson(self, ctx:JSONParser.JsonContext):
        pass


    # Enter a parse tree produced by JSONParser#AnObject.
    def enterAnObject(self, ctx:JSONParser.AnObjectContext):
        global DictionaryLevel
        DictionaryLevel = DictionaryLevel + 1
        if DictionaryLevel == 1:
            print('top =')
        print(DictionaryLevel*'\t' + '\n' + DictionaryLevel*'\t'+'{')
        print(DictionaryLevel*'\t' + '"LEVEL":' + str(DictionaryLevel))


    # Exit a parse tree produced by JSONParser#AnObject.
    def exitAnObject(self, ctx:JSONParser.AnObjectContext):
        global DictionaryLevel
        DictionaryLevel = DictionaryLevel - 1
        print(DictionaryLevel*'\t' + '}')


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
        print('[', end=' ')

    # Exit a parse tree produced by JSONParser#ArrayOfValues.
    def exitArrayOfValues(self, ctx:JSONParser.ArrayOfValuesContext):
        global InArrayFlag
        InArrayFlag = False
        print(']')

    # Enter a parse tree produced by JSONParser#EmptyArray.
    def enterEmptyArray(self, ctx:JSONParser.EmptyArrayContext):
        print("[]")

    # Exit a parse tree produced by JSONParser#EmptyArray.
    def exitEmptyArray(self, ctx:JSONParser.EmptyArrayContext):
        pass


    # Enter a parse tree produced by JSONParser#pair.
    def enterPair(self, ctx:JSONParser.PairContext):
        s = ctx.STRING().getText()
        global DictionaryLevel
        print()
        print(DictionaryLevel*'\t' + s + ":", end='')

    # Exit a parse tree produced by JSONParser#pair.
    def exitPair(self, ctx:JSONParser.PairContext):
        pass


    # Enter a parse tree produced by JSONParser#String.
    def enterString(self, ctx:JSONParser.StringContext):
        global InArrayFlag
        end = ' ' if InArrayFlag else '\n'
        print(ctx.getText(), end=end)

    # Exit a parse tree produced by JSONParser#String.
    def exitString(self, ctx:JSONParser.StringContext):
        pass


    # Enter a parse tree produced by JSONParser#Atom.
    def enterAtom(self, ctx:JSONParser.AtomContext):
        pass

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
    input_stream = FileStream(sys.argv[1])
    #  input_stream = StdinStream()
    #  input_stream = InputStream(<string>)
    lexer = Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JSONParser(stream)
    tree = parser.json()
    printer = JSONPrintListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

if __name__ == '__main__':
    main()