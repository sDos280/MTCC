import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('parameter_declaration.c')
lexer.lex()

parser = Parser.mtcc_parser.Parser(lexer.tokens, lexer.file_string)

for i in range(4):
    declarator: Parser.mtcc_c_ast.CDeclarator = parser.peek_parameter_declaration()
    print(f"parameter {i + 1}: AST: ")
    print(json.dumps(declarator.to_dict(), indent=2), end='\n\n')
    parser.peek_token()  # peek ; token
