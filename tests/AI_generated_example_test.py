import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('AI_generated_example.c')
lexer.lex()

parser = Parser.mtcc_parser.Parser(lexer.tokens, lexer.file_string)

translation_unit = parser.peek_translation_unit()

print(f"translation unit: AST: ")
for external_declaration in translation_unit:
    if not isinstance(external_declaration, list):
        print(json.dumps(external_declaration.to_dict(), indent=2), end='\n\n')
    else:
        for declaration in external_declaration:
            print(json.dumps(declaration.to_dict(), indent=2), end='\n\n')
