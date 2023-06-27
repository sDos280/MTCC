import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('type_name.c')
lexer.lex()

parser = Parser.mtcc_parser.CParser(lexer.tokens, lexer.file_string)

for i in range(2):
    type_name: Parser.mtcc_c_ast.CTypeName = parser.peek_type_name()
    print(f"type name {i + 1}: AST: ")
    print(json.dumps(type_name.to_dict(), indent=2), end='\n\n')
