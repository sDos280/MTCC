import Parser.mtcc_lexer
import Parser.mtcc_token

lexer = Parser.mtcc_lexer.Lexer('escape_sequence.c')
lexer.lex()

for index, escape_sequence in enumerate(lexer.tokens):
    print(f"comment {index + 1}: Lexer: ")
    print(escape_sequence.string, end='\n\n')
