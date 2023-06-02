import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('type_name.c')
lexer.lex()

parser = Parser.mtcc_parser.Parser(lexer.tokens, lexer.file_string)

type_name: Parser.mtcc_c_ast.CTypeName = parser.peek_type_name()
print("type name 1: AST: ")
print(json.dumps(type_name.to_dict(), indent=2))

type_name: Parser.mtcc_c_ast.CTypeName = parser.peek_type_name()
print("type name 2: AST: ")
print(json.dumps(type_name.to_dict(), indent=2))
