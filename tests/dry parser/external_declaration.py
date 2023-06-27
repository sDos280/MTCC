import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('external_declaration.c')
lexer.lex()

parser = Parser.mtcc_parser.CParser(lexer.tokens, lexer.file_string)

for i in range(2):
    external_declaration: list[Parser.mtcc_c_ast.CDeclarator] | Parser.mtcc_c_ast.CDeclarator = parser.peek_external_declaration()
    print(f"external declaration {i + 1}: AST: ")
    if isinstance(external_declaration, list):
        for sub_declarator in external_declaration:
            print(json.dumps(sub_declarator.to_dict(), indent=2), end='\n\n')
    else:
        print(json.dumps(external_declaration.to_dict(), indent=2), end='\n\n')
