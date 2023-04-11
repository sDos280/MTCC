import sys
import Parser.mtcc_lexer
import Parser.mtcc_parser
import pathlib


if __name__ == '__main__':
    lexer = Parser.mtcc_lexer.lexer(pathlib.Path(sys.argv[0]).parent / sys.argv[1])
    lexer.lex()

    parser = Parser.mtcc_parser.Parser(lexer.tokens)

    parser.parse()

    [print(i) for i in parser.enums]
