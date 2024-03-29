import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_ast_validator
import json

lexer = Parser.mtcc_lexer.Lexer('AI_generated_example.c')
lexer.lex()

parser = Parser.mtcc_parser.CParser(lexer.tokens, lexer.file_string)

translation_unit = parser.peek_translation_unit()

print(f"translation unit: AST: ")
for external_declaration in translation_unit:
    print(json.dumps(external_declaration.to_dict(), indent=2), end='\n\n')

validator = Parser.mtcc_ast_validator.AstValidator(parser, translation_unit)
