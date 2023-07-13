import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_ast_validator
import json

lexer = Parser.mtcc_lexer.Lexer('duplicate_identifier.c')
lexer.lex()

parser = Parser.mtcc_parser.CParser(lexer.tokens, lexer.file_string)

translation_unit = parser.peek_translation_unit()

print(f"duplicate identifier: AST: ")
for external_declaration in translation_unit:
    print(json.dumps(external_declaration.to_dict(), indent=2), end='\n\n')

validator = Parser.mtcc_ast_validator.AstValidator(parser, translation_unit)
validator.push_translation_unit_identifiers()
