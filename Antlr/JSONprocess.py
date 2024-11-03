from antlr4 import *
from JSONLexer import JSONLexer as Lexer
from JSONListener import JSONListener as Listener
from JSONParser import JSONParser as JSONParser
import sys

class JSONPrintListener(Listener):
    # Enter a parse tree produced by JSONParser#json.
    def enterJson(self, ctx:JSONParser.JsonContext):
        print('enterJson')

    # Exit a parse tree produced by JSONParser#json.
    def exitJson(self, ctx:JSONParser.JsonContext):
        print('exitJson')


    # Enter a parse tree produced by JSONParser#AnObject.
    def enterAnObject(self, ctx:JSONParser.AnObjectContext):
        pass

    # Exit a parse tree produced by JSONParser#AnObject.
    def exitAnObject(self, ctx:JSONParser.AnObjectContext):
        pass


    # Enter a parse tree produced by JSONParser#EmptyObject.
    def enterEmptyObject(self, ctx:JSONParser.EmptyObjectContext):
        pass

    # Exit a parse tree produced by JSONParser#EmptyObject.
    def exitEmptyObject(self, ctx:JSONParser.EmptyObjectContext):
        pass


    # Enter a parse tree produced by JSONParser#ArrayOfValues.
    def enterArrayOfValues(self, ctx:JSONParser.ArrayOfValuesContext):
        pass

    # Exit a parse tree produced by JSONParser#ArrayOfValues.
    def exitArrayOfValues(self, ctx:JSONParser.ArrayOfValuesContext):
        pass


    # Enter a parse tree produced by JSONParser#EmptyArray.
    def enterEmptyArray(self, ctx:JSONParser.EmptyArrayContext):
        pass

    # Exit a parse tree produced by JSONParser#EmptyArray.
    def exitEmptyArray(self, ctx:JSONParser.EmptyArrayContext):
        pass


    # Enter a parse tree produced by JSONParser#pair.
    def enterPair(self, ctx:JSONParser.PairContext):
        s = ctx.STRING().getText()
        v = ctx.value()

    # Exit a parse tree produced by JSONParser#pair.
    def exitPair(self, ctx:JSONParser.PairContext):
        pass


    # Enter a parse tree produced by JSONParser#String.
    def enterString(self, ctx:JSONParser.StringContext):
        pass

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