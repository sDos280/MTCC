import sys
import Parser.tmcc_lexer
import pathlib

def main():
    print("fgsdfgsdfg")

if __name__ == '__main__':
    lexer = Parser.tmcc_lexer.lexer(pathlib.Path(sys.argv[0]).parent / sys.argv[1])
    lexer.lex()

    [print(lexer.get_token_string(i)) for i in lexer.tokens]

