import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('declaration.c')
lexer.lex()

parser = Parser.mtcc_parser.Parser(lexer.tokens, lexer.file_string)

for i in range(5):
    declarator: list[Parser.mtcc_c_ast.CDeclarator] = parser.peek_declaration()
    print(f"pointer {i + 1}: AST: ")
    for sub_declarator in declarator:
        print(json.dumps(sub_declarator.to_dict(), indent=2), end='\n\n')
