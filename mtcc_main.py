import sys
import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_error_handler
import pathlib


if __name__ == '__main__':
    lexer = Parser.mtcc_lexer.Lexer(pathlib.Path(sys.argv[0]).parent / sys.argv[1])
    lexer.lex()

    # [print(token.string) for token in lexer.tokens]

    parser = Parser.mtcc_parser.CParser(lexer.tokens, lexer.file_string)

    parser.translation_unit()
