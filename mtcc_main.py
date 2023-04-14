import sys
import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_error_handler
import pathlib


if __name__ == '__main__':
    lexer = Parser.mtcc_lexer.Lexer(pathlib.Path(sys.argv[0]).parent / sys.argv[1])
    lexer.lex()

    error_handler = Parser.mtcc_error_handler.ErrorHandler(lexer)

    parser = Parser.mtcc_parser.Parser(lexer.tokens, error_handler)

    parser.parse()

    [print(i) for i in parser.typedefs]
