import sys
import Parser.tmcc_lexer
import Parser.tmcc_parser
import pathlib

def main():
    print("fgsdfgsdfg")

if __name__ == '__main__':
    lexer = Parser.tmcc_lexer.lexer(pathlib.Path(sys.argv[0]).parent / sys.argv[1])
    lexer.lex()

    parser = Parser.tmcc_parser.parser(lexer.tokens, lexer)

    parser.parse()

    print(parser.abstract_syntax_tree)
