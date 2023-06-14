import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('struct_or_union.c')
lexer.lex()

parser = Parser.mtcc_parser.Parser(lexer.tokens, lexer.file_string)

for i in range(4):
    struct_or_union: Parser.mtcc_c_ast.CStruct | Parser.mtcc_c_ast.CUnion = parser.peek_struct_or_union_specifier()
    print(f"struct_or_union {i + 1}: AST: ")
    print(json.dumps(struct_or_union.to_dict(), indent=2), end='\n\n')
    parser.peek_token()  # peek ; token
