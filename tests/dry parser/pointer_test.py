import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('pointer.c')
lexer.lex()

parser = Parser.mtcc_parser.CParser(lexer.tokens, lexer.file_string)

for i in range(2):
    pointer: Parser.mtcc_c_ast.CPointer = parser.peek_pointer()
    print(f"pointer {i + 1}: AST: ")
    print(json.dumps(pointer.to_dict(), indent=2), end='\n\n')
    parser.peek_token()  # peek ; token
