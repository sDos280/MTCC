import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('statement.c')
lexer.lex()

parser = Parser.mtcc_parser.Parser(lexer.tokens, lexer.file_string)

for i in range(4):
    statement: Parser.mtcc_c_ast.Node = parser.peek_statement()
    print(f"statement {i + 1}: AST: ")
    print(json.dumps(statement.to_dict(), indent=2), end='\n\n')

