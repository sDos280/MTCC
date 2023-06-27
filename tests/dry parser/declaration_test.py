import Parser.mtcc_lexer
import Parser.mtcc_parser
import Parser.mtcc_c_ast
import json

lexer = Parser.mtcc_lexer.Lexer('declaration.c')
lexer.lex()

parser = Parser.mtcc_parser.CParser(lexer.tokens, lexer.file_string)

for i in range(5):
    declarator: list[Parser.mtcc_c_ast.CDeclarator] = parser.peek_declaration()
    type_attributes: Parser.mtcc_c_ast.CTypeAttribute = declarator[0].attributes
    if type_attributes.storage_class_specifier == Parser.mtcc_c_ast.CStorageClassSpecifier.Typedef:
        parser.typedefs.append(Parser.mtcc_c_ast.CTypedef(declarator[0]))

    print(f"declaration {i + 1}: AST: ")
    for sub_declarator in declarator:
        print(json.dumps(sub_declarator.to_dict(), indent=2), end='\n\n')
