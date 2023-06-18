import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('enum.c')
lexer.lex()

parser = Parser.mtcc_parser.Parser(lexer.tokens, lexer.file_string)

for i in range(2):
    enum: Parser.mtcc_c_ast.CEnum = parser.peek_enum_specifier()
    print(f"enum {i + 1}: AST: ")
    print(json.dumps(enum.to_dict(), indent=2), end='\n\n')
    parser.peek_token()  # peek ; token
