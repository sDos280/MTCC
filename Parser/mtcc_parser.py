from __future__ import annotations

import Parser.mtcc_error_handler as eh
from Parser.mtcc_c_ast import *


class Parser:
    def __init__(self, tokens: list[tk.Token], source_string: str):
        self.tokens: list[tk.Token] = tokens
        for token_index in range(len(self.tokens)):
            self.tokens[token_index].index = token_index
        self.index: int = 0
        self.current_token: tk.Token = self.tokens[self.index]

        self.source_string: str = source_string

        self.current_block: Block | None = None

        self.enums: list[CEnum] = []
        self.typedefs: list[CTypedef] = []
        self.variables: list[Variable] = []  # variables declension list
        self.function_declension: list[CFunction] = []
        self.function: list[CFunction]  # functions ast code

    def peek_token(self) -> None:  # increase the index and update the current token
        self.index += 1
        self.current_token = self.tokens[self.index]

    def drop_token(self) -> None:  # decrease the index and update the current token
        self.index -= 1
        self.current_token = self.tokens[self.index]

    def set_index_token(self, index: int) -> None:
        self.index = index
        self.current_token = self.tokens[self.index]

    def is_token_kind(self, kind: list[tk.TokenKind] | tk.TokenKind) -> bool:
        if isinstance(kind, tk.TokenKind):
            return self.current_token.kind == kind
        else:
            return self.current_token.kind in kind

    def is_token_storage_class_specifier(self) -> bool:
        return self.is_token_kind(
            [tk.TokenKind.TYPEDEF,
             tk.TokenKind.EXTERN,
             tk.TokenKind.STATIC,
             tk.TokenKind.AUTO,
             tk.TokenKind.REGISTER])

    def is_token_type_specifier(self) -> bool:
        return self.is_token_kind(
            [tk.TokenKind.VOID,
             tk.TokenKind.CHAR,
             tk.TokenKind.SHORT,
             tk.TokenKind.INT,
             tk.TokenKind.LONG,
             tk.TokenKind.FLOAT,
             tk.TokenKind.DOUBLE,
             tk.TokenKind.SIGNED,
             tk.TokenKind.UNSIGNED,
             tk.TokenKind.STRUCT,
             tk.TokenKind.UNION,
             tk.TokenKind.ENUM,
             tk.TokenKind.IDENTIFIER])

    def is_token_type_qualifier(self) -> bool:
        return self.is_token_kind(
            [tk.TokenKind.CONST,
             tk.TokenKind.VOLATILE])

    def get_line_string(self, line: int) -> str:
        lines: list[str] = self.source_string.split('\n')
        if line <= len(lines):
            return lines[line]
        else:
            return ""

    def get_line_substring_at_index(self, index: int) -> str:
        # find the beginning of the line containing the index
        start_of_line = self.source_string.rfind('\n', 0, index) + 1 if '\n' in self.source_string[:index] else 0
        return self.source_string[start_of_line:index]

    def fatal_token(self, token_location: int, error_string: str, raise_exception) -> None:
        line_string: str = self.get_line_string(self.tokens[token_location].line)
        sub_line_string: str = self.get_line_substring_at_index(
            self.tokens[token_location].start)  # the sub line right up to the token start
        full_error_string: str = f"\nMTCC:{self.tokens[token_location].line + 1}:{len(sub_line_string) + 1}: "
        full_error_string += error_string + '\n'
        full_error_string += f"    | {line_string}\n"
        full_error_string += f"    | {len(sub_line_string) * ' '}^{(len(self.tokens[token_location].string) - 1) * '~'}"
        raise raise_exception(full_error_string)

    def expect_token_kind(self, kind: list[tk.TokenKind] | tk.TokenKind, error_string: str, raise_exception) -> None:
        if not self.is_token_kind(kind):
            self.fatal_token(self.index, error_string, raise_exception)

    def is_abstract_declarator(self) -> bool:
        """check if the current token is an abstract declarator starter"""
        return self.is_token_kind(
            [tk.TokenKind.ASTERISK, tk.TokenKind.OPENING_PARENTHESIS, tk.TokenKind.OPENING_BRACKET])

    def is_direct_abstract_declarator(self) -> bool:
        """check if the current token is a direct abstract declarator starter"""
        return self.is_token_kind([tk.TokenKind.OPENING_PARENTHESIS, tk.TokenKind.OPENING_BRACKET])

    def is_direct_declarator(self) -> bool:
        """check if the current token is a direct declarator starter"""
        return self.is_token_kind([tk.TokenKind.IDENTIFIER, tk.TokenKind.OPENING_PARENTHESIS, tk.TokenKind.OPENING_BRACKET])

    def is_declarator(self) -> bool:
        """check if the current token is a declarator starter"""
        return self.is_token_kind([tk.TokenKind.ASTERISK, tk.TokenKind.IDENTIFIER, tk.TokenKind.OPENING_PARENTHESIS, tk.TokenKind.OPENING_BRACKET])

    def is_typedef_name(self, name: str) -> bool:
        for typedef in self.typedefs:
            if typedef.name.token.string == name:
                return True
        return False

    def peek_type_qualifier(self) -> CQualifierKind:
        self.expect_token_kind([tk.TokenKind.CONST, tk.TokenKind.VOLATILE], "Expected a type qualifier token",
                               eh.TypeQualifierNotFound)

        qualifier: CQualifierKind = CQualifierKind(0)

        if self.is_token_kind(tk.TokenKind.CONST):
            qualifier = CQualifierKind.Const
        elif self.is_token_kind(tk.TokenKind.VOLATILE):
            qualifier = CQualifierKind.Volatile

        self.peek_token()  # peek qualifier token

        return qualifier

    def peek_type_specifier(self) -> CSpecifierKind:
        self.expect_token_kind(
            [
                tk.TokenKind.VOID,
                tk.TokenKind.CHAR,
                tk.TokenKind.SHORT,
                tk.TokenKind.INT,
                tk.TokenKind.LONG,
                tk.TokenKind.FLOAT,
                tk.TokenKind.DOUBLE,
                tk.TokenKind.SIGNED,
                tk.TokenKind.UNSIGNED,
                tk.TokenKind.STRUCT,
                tk.TokenKind.UNION,
                tk.TokenKind.ENUM,
                tk.TokenKind.IDENTIFIER
            ],
            "Expected a type specifier token",
            eh.TypeSpecifierNotFound
        )
        specifier: CSpecifierKind = CSpecifierKind(0)

        if self.is_token_kind(tk.TokenKind.VOID):
            specifier = CSpecifierKind.Void
        elif self.is_token_kind(tk.TokenKind.SHORT):
            specifier = CSpecifierKind.Short
        elif self.is_token_kind(tk.TokenKind.CHAR):
            specifier = CSpecifierKind.Char
        elif self.is_token_kind(tk.TokenKind.INT):
            specifier = CSpecifierKind.Int
        elif self.is_token_kind(tk.TokenKind.LONG):
            specifier = CSpecifierKind.Long
        elif self.is_token_kind(tk.TokenKind.FLOAT):
            specifier = CSpecifierKind.Float
        elif self.is_token_kind(tk.TokenKind.DOUBLE):
            specifier = CSpecifierKind.Double
        elif self.is_token_kind(tk.TokenKind.SIGNED):
            specifier = CSpecifierKind.Signed
        elif self.is_token_kind(tk.TokenKind.UNSIGNED):
            specifier = CSpecifierKind.Unsigned

        self.peek_token()  # peek specifier token

        return specifier

    def peek_storage_class_specifier(self) -> CStorageClassSpecifier:
        """
        parse a storage class specifier
        storage_class_specifier
            : TYPEDEF
            | EXTERN
            | STATIC
            | AUTO
            | REGISTER
            ;
        :return:  a storage class specifier node
        """
        self.expect_token_kind(
            [
                tk.TokenKind.TYPEDEF,
                tk.TokenKind.EXTERN,
                tk.TokenKind.STATIC,
                tk.TokenKind.AUTO,
                tk.TokenKind.REGISTER
            ],
            "Expected a storage class specifier token",
            eh.TokenExpected
        )

        storage_class_specifier: CStorageClassSpecifier = CStorageClassSpecifier(0)
        if self.is_token_kind(tk.TokenKind.TYPEDEF):
            storage_class_specifier = CStorageClassSpecifier.Typedef
        elif self.is_token_kind(tk.TokenKind.EXTERN):
            storage_class_specifier = CStorageClassSpecifier.Extern
        elif self.is_token_kind(tk.TokenKind.STATIC):
            storage_class_specifier = CStorageClassSpecifier.Static
        elif self.is_token_kind(tk.TokenKind.AUTO):
            storage_class_specifier = CStorageClassSpecifier.Auto
        elif self.is_token_kind(tk.TokenKind.REGISTER):
            storage_class_specifier = CStorageClassSpecifier.Register

        self.peek_token()  # peek storage class specifier token

        return storage_class_specifier

    def peek_specifier_qualifier_list(self) -> CSpecifierType:
        """
        parse a specifier qualifier list
        specifier_qualifier_list
            : type_specifier specifier_qualifier_list
            | type_specifier
            | type_qualifier specifier_qualifier_list
            | type_qualifier
            ;
        :return: a specifier type node
        """

        # the idea is form https://github.com/sgraham/dyibicc/blob/main/src/parse.c#L359
        specifier_counter: CSpecifierKind = CSpecifierKind(0)
        qualifier_counter: CQualifierKind = CQualifierKind(0)
        type: CSpecifierType = NoneNode()

        while self.is_token_type_specifier() or self.is_token_type_qualifier():
            # handel qualifiers
            # TODO: make a way that those qualifiers will be really used
            if self.is_token_type_qualifier():
                qualifier_counter |= self.peek_type_qualifier()

            # handle struct, union, enum and typename identifier
            # when parsing those specifiers the specifier count should be 0
            if self.is_token_kind(tk.TokenKind.STRUCT) or \
                    self.is_token_kind(tk.TokenKind.UNION) or \
                    self.is_token_kind(tk.TokenKind.ENUM) or \
                    self.is_token_kind(tk.TokenKind.IDENTIFIER):
                # TODO: each if the identifier is typedef, if not break
                if self.is_token_kind(tk.TokenKind.IDENTIFIER) and self.is_typedef_name(self.current_token.string):
                    if specifier_counter != 0:
                        self.fatal_token(self.current_token.index, "Invalid specifier in that current contex",
                                         eh.SpecifierQualifierListInvalid)

                    # TODO: implement and return the CSpecifierType
                    if self.is_token_kind(tk.TokenKind.STRUCT):
                        assert False, "Not implemented"
                    elif self.is_token_kind(tk.TokenKind.UNION):
                        assert False, "Not implemented"
                    elif self.is_token_kind(tk.TokenKind.ENUM):
                        assert False, "Not implemented"
                    elif self.is_token_kind(tk.TokenKind.IDENTIFIER):
                        assert False, "Not implemented"
                else:
                    return type

            current_specifier_kind: CSpecifierKind = self.peek_type_specifier()
            if current_specifier_kind == CSpecifierKind.Signed or \
                    current_specifier_kind == current_specifier_kind.Unsigned:
                specifier_counter |= current_specifier_kind
            else:
                specifier_counter += current_specifier_kind

            specifier_type: CPrimitiveDataTypes = specifier_cases.get(specifier_counter)

            if specifier_type is None:
                self.fatal_token(self.current_token.index,
                                 "Invalid specifier in that current contex",
                                 eh.SpecifierQualifierListInvalid
                                 )
            else:
                type = specifier_type

        if isinstance(type, NoneNode):
            self.fatal_token(self.current_token.index,
                             "Invalid specifier in that current contex",
                             eh.SpecifierQualifierListInvalid
                             )
        else:
            return type

    def peek_type_name(self) -> CTypeName:
        """
        parse a type name
        type_name
            : specifier_qualifier_list
            | specifier_qualifier_list abstract_declarator
            ;
        :return: a type name node
        """
        specified_qualifier: CSpecifierType = self.peek_specifier_qualifier_list()

        abstract_declarator: CType = NoneNode()
        if self.is_abstract_declarator():
            abstract_declarator: CType = self.peek_abstract_declarator()
            abstract_declarator.get_child_bottom().child = specified_qualifier

        return CTypeName(abstract_declarator if not isinstance(abstract_declarator, NoneNode) else specified_qualifier)

    def peek_declaration_specifiers(self) -> CSpecifierType:
        """
        parse a declaration specifier
        declaration_specifiers
            : storage_class_specifier
            | storage_class_specifier declaration_specifiers
            | type_specifier
            | type_specifier declaration_specifiers
            | type_qualifier
            | type_qualifier declaration_specifiers
            ;
        :return: a specifier type node
        """
        # the idea is form https://github.com/sgraham/dyibicc/blob/main/src/parse.c#L359
        storage_class_specifier_counter: CStorageClassSpecifier = CStorageClassSpecifier(0)
        specifier_counter: CSpecifierKind = CSpecifierKind(0)
        qualifier_counter: CQualifierKind = CQualifierKind(0)
        type: CSpecifierType = NoneNode()

        while self.is_token_storage_class_specifier() or self.is_token_type_specifier() or self.is_token_type_qualifier():
            # handle storage class specifiers
            # TODO: make a way that those qualifiers will be really used
            if self.is_token_storage_class_specifier():
                storage_class_specifier_counter |= self.peek_storage_class_specifier()

            # handel qualifiers
            # TODO: make a way that those qualifiers will be really used
            if self.is_token_type_qualifier():
                qualifier_counter |= self.peek_type_qualifier()

            # handle struct, union, enum and typename identifier
            # when parsing those specifiers the specifier count should be 0
            if self.is_token_kind(tk.TokenKind.STRUCT) or \
                    self.is_token_kind(tk.TokenKind.UNION) or \
                    self.is_token_kind(tk.TokenKind.ENUM) or \
                    self.is_token_kind(tk.TokenKind.IDENTIFIER):
                if specifier_counter != 0:
                    self.fatal_token(self.current_token.index, "Invalid specifier in that current contex",
                                     eh.SpecifierQualifierListInvalid)

                # TODO: implement and return the CSpecifierType
                if self.is_token_kind(tk.TokenKind.STRUCT):
                    assert False, "Not implemented"
                elif self.is_token_kind(tk.TokenKind.UNION):
                    assert False, "Not implemented"
                elif self.is_token_kind(tk.TokenKind.ENUM):
                    assert False, "Not implemented"
                elif self.is_token_kind(tk.TokenKind.IDENTIFIER):
                    assert False, "Not implemented"

            current_specifier_kind: CSpecifierKind = self.peek_type_specifier()
            if current_specifier_kind == CSpecifierKind.Signed or current_specifier_kind == current_specifier_kind.Unsigned:
                specifier_counter |= current_specifier_kind
            else:
                specifier_counter += current_specifier_kind

            specifier_type: CPrimitiveDataTypes = specifier_cases.get(specifier_counter)

            if specifier_type is None:
                self.fatal_token(self.current_token.index,
                                 "Invalid specifier in that current contex",
                                 eh.SpecifierQualifierListInvalid
                                 )
            else:
                type = specifier_type

        if isinstance(type, NoneNode):
            self.fatal_token(self.current_token.index,
                             "Invalid specifier in that current contex",
                             eh.SpecifierQualifierListInvalid
                             )
        else:
            return type

    def peek_type_qualifier_list(self) -> CQualifierKind:
        """
        parse a type qualifier list
        type_qualifier_list
            : type_qualifier
            | type_qualifier_list type_qualifier
            ;
        :return: a qualifier kind node
        """
        qualifier_counter: CQualifierKind = CQualifierKind(0)
        while self.is_token_type_qualifier():
            if self.is_token_kind(tk.TokenKind.CONST):
                qualifier_counter |= CQualifierKind.Const
            elif self.is_token_kind(tk.TokenKind.VOLATILE):
                qualifier_counter |= CQualifierKind.Volatile
            self.peek_token()  # peek the qualifier token

        return qualifier_counter

    def peek_pointer(self) -> CPointer:
        """
        parse a pointer
        pointer
            : '*'
            | '*' type_qualifier_list
            | '*' pointer
            | '*' type_qualifier_list pointer
            ;
        :return: a pointer node
        """
        pointer: CPointer = CPointer(0, CQualifierKind(0), NoneNode())
        pointer_counter: int = 0

        while self.is_token_kind(tk.TokenKind.ASTERISK):
            pointer_counter += 1
            self.peek_token()  # peek * token

        pointer.pointer_level = pointer_counter
        if self.is_token_type_qualifier():
            pointer.qualifiers = self.peek_type_qualifier_list()

        if self.is_token_kind(tk.TokenKind.ASTERISK):
            pointer.child = self.peek_pointer()

        return pointer

    def peek_direct_declarator_module(self) -> Node | list[CParameter]:
        """
        parse a direct declarator module
        direct_declarator_module
                    : '(' declarator ')'
                    | '[' constant_expression ']'
                    | '[' ']'
                    | '(' parameter_type_list ')'
                    | '(' ')'
                    ;
        :return: a direct declarator module node
        """
        if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek ( token
            if self.is_token_kind(tk.TokenKind.CLOSING_PARENTHESIS):
                self.peek_token()  # peek ) token
                return list[CParameter]()

            if self.is_token_type_specifier() or self.is_token_type_qualifier():
                parameter_type_list: list[CParameter] = self.peek_parameter_type_list()

                self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected closing parenthesis", eh.TokenExpected)
                self.peek_token()  # peek ) token

                return parameter_type_list
            else:
                declarator: CDeclarator = self.peek_declarator()

                self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected closing parenthesis", eh.TokenExpected)
                self.peek_token()  # peek ) token

                return declarator

        elif self.is_token_kind(tk.TokenKind.OPENING_BRACKET):
            self.peek_token()  # peek [ token
            if self.is_token_kind(tk.TokenKind.CLOSING_BRACKET):
                self.peek_token()  # peek ] token
                return CArray(NoneNode(), NoneNode())

            constant_expression: Node = self.peek_constant_expression()

            self.expect_token_kind(tk.TokenKind.CLOSING_BRACKET, "Expected closing bracket", eh.TokenExpected)
            self.peek_token()  # peek ] token

            return CArray(constant_expression, NoneNode())
        else:
            self.fatal_token(self.current_token.index,
                             "Expected opening parenthesis or opening bracket",
                             eh.TokenExpected
                             )

    def peek_direct_declarator(self) -> CDeclarator:
        """
        parse a direct declarator, if no IDENTIFIER is found, it will return an empty named direct declarator
        direct_declarator
            : IDENTIFIER
            | '(' declarator ')'
            | direct_declarator '[' constant_expression ']'
            | direct_declarator '[' ']'
            | direct_declarator '(' parameter_type_list ')'
            | direct_declarator '(' identifier_list ')'   # we would not support this
            | direct_declarator '(' ')'
            ;
        :return: a direct declarator node
        """
        identifier: CIdentifier | NoneNode = NoneNode()
        if self.is_direct_declarator():
            if self.is_token_kind(tk.TokenKind.IDENTIFIER):
                identifier = CIdentifier(self.current_token)
                self.peek_token()  # peek the identifier token
            elif self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
                self.peek_token()  # peek the ( token

                declarator: CDeclarator = self.peek_declarator()

                self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected closing parenthesis", eh.TokenExpected)
                self.peek_token()  # peek the ) token

                return declarator
        else:
            self.fatal_token(self.current_token.index,
                             "Expected identifier or opening parenthesis",
                             eh.TokenExpected
                             )

        declarator: CDeclarator = CDeclarator(identifier, NoneNode())

        if not self.is_direct_abstract_declarator():
            return declarator

        direct_declarator_module: Node | list[CParameter] = self.peek_direct_declarator_module()

        if isinstance(direct_declarator_module, list):  # need to convert direct_declarator_module to CFunction
            direct_declarator_module = CFunction(NoneNode(), direct_declarator_module, NoneNode())

        declarator.type = direct_declarator_module

        while True:
            if self.is_direct_abstract_declarator():
                direct_abstract_declarator_module: CType = self.peek_direct_abstract_declarator_module()
                if isinstance(direct_abstract_declarator_module, list):  # need to convert direct_abstract_declarator_module to CFunction
                    declarator.get_child_bottom().child = CFunction(NoneNode(), direct_abstract_declarator_module, NoneNode())
                else:
                    declarator.get_child_bottom().child = direct_abstract_declarator_module
            else:
                return declarator

    def peek_declarator(self) -> CDeclarator:
        """
        parse a declarator
        declarator
            : pointer direct_declarator
            | direct_declarator
            ;
        :return: a declarator node
        """
        pointer: CPointer | NoneNode = NoneNode()
        if self.is_token_kind(tk.TokenKind.ASTERISK):
            pointer = self.peek_pointer()

        direct_declarator: CDeclarator = self.peek_direct_declarator()

        if not isinstance(pointer, NoneNode):
            direct_declarator.get_child_bottom().child = pointer
        return direct_declarator

    def peek_parameter_declaration(self) -> CParameter:
        """
        parse a parameter declaration
        parameter_declaration
            : declaration_specifiers declarator
            | declaration_specifiers abstract_declarator
            | declaration_specifiers
        :return: a parameter declaration node
        """
        declaration_specifiers: CSpecifierType = self.peek_specifier_qualifier_list()

        if not (self.is_abstract_declarator() or self.is_declarator()):
            return CParameter(CIdentifier(None), declaration_specifiers)

        declarator_or_abstract_declarator: CDeclarator | NoneNode = self.peek_declarator()

        if not isinstance(declarator_or_abstract_declarator, NoneNode):
            declarator_or_abstract_declarator.get_child_bottom().child = declaration_specifiers

            return declarator_or_abstract_declarator
        else:
            self.fatal_token(self.current_token.index,
                             "Expected declarator or abstract declarator",
                             eh.TokenExpected
                             )

    def peek_parameter_type_list(self) -> list[CParameter]:
        """
        parse a parameter type list
        parameter_type_list
            : parameter_list ',' ELLIPSIS
            | parameter_list
            ;
        :return: a list of parameter nodes
        """
        parameter_list: list[CParameter] = []
        while True:
            if self.is_token_storage_class_specifier() or self.is_token_type_specifier() or self.is_token_type_qualifier():
                parameter_declaration: CParameter = self.peek_parameter_declaration()
                parameter_list.append(parameter_declaration)
                if self.is_token_kind(tk.TokenKind.COMMA):
                    self.peek_token()
            elif self.is_token_kind(tk.TokenKind.ELLIPSIS):
                assert False, "Not implemented"
            else:
                return parameter_list

    def peek_abstract_declarator(self) -> CType:
        """
        parse an abstract declarator
        abstract_declarator
            : pointer
            | direct_abstract_declarator
            | pointer direct_abstract_declarator
            ;
        :return: an abstract declarator node
        """
        if self.is_direct_abstract_declarator():
            return self.peek_direct_abstract_declarator()
        elif self.is_token_kind(tk.TokenKind.ASTERISK):
            pointer_level: int = 0
            while self.is_token_kind(tk.TokenKind.ASTERISK):
                self.peek_token()  # peek * token
                pointer_level += 1

            if self.is_direct_abstract_declarator():
                direct_abstract_declarator: CType = self.peek_direct_abstract_declarator()
                direct_abstract_declarator.get_child_bottom().child = CPointer(pointer_level, CQualifierKind(0), NoneNode())
                return direct_abstract_declarator
            else:
                return CPointer(pointer_level, CQualifierKind(0), NoneNode())

    def peek_direct_abstract_declarator(self) -> CType:
        # return the top and bottom of the direct abstract declarator
        direct_abstract_declarator_module: CType = self.peek_direct_abstract_declarator_module()
        if isinstance(direct_abstract_declarator_module, list):  # need to convert direct_abstract_declarator_module to CFunction
            direct_abstract_declarator_module = CFunction(NoneNode(), direct_abstract_declarator_module, NoneNode())
        direct_abstract_declarator: CType = direct_abstract_declarator_module

        while True:
            if self.is_direct_abstract_declarator():
                direct_abstract_declarator_module: CType = self.peek_direct_abstract_declarator_module()
                if isinstance(direct_abstract_declarator_module, list):  # need to convert direct_abstract_declarator_module to CFunction
                    direct_abstract_declarator.get_child_bottom().child = CFunction(NoneNode(), direct_abstract_declarator_module, NoneNode())
                else:
                    direct_abstract_declarator.get_child_bottom().child = direct_abstract_declarator_module
            else:
                return direct_abstract_declarator

    def peek_direct_abstract_declarator_module(self) -> CType | list[CParameter]:
        """
        parse a direct abstract declarator module
        direct_abstract_declarator_module
            : '(' abstract_declarator ')'
            | '[' ']'
            | '[' constant_expression ']'
            | '(' ')'
            | '(' parameter_type_list ')'
            ;
        :return: a direct abstract declarator module node
        """
        if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek ( token
            if self.is_token_kind(tk.TokenKind.CLOSING_PARENTHESIS):
                self.peek_token()  # peek ) token

                return list[CParameter]()
            else:
                if self.is_token_type_specifier() or self.is_token_type_qualifier():
                    parameter_type_list: list[CParameter] = self.peek_parameter_type_list()
                    self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected a ) token", eh.TokenExpected)
                    self.peek_token()  # peek ) token

                    return parameter_type_list
                else:
                    abstract_declarator: CType = self.peek_abstract_declarator()
                    self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected a ) token", eh.TokenExpected)
                    self.peek_token()  # peek ) token

                    return abstract_declarator
        elif self.is_token_kind(tk.TokenKind.OPENING_BRACKET):
            self.peek_token()  # peek [ token
            if self.is_token_kind(tk.TokenKind.CLOSING_BRACKET):
                self.peek_token()  # peek ] token

                return CArray(NoneNode(), NoneNode())
            else:
                constant_expression: Node = self.peek_constant_expression()
                self.expect_token_kind(tk.TokenKind.CLOSING_BRACKET, "Expected a ] token", eh.TokenExpected)
                self.peek_token()  # peek ] token
                return CArray(constant_expression, NoneNode())
        else:
            self.fatal_token(self.current_token.index, "Expected a ( or [ token", eh.TokenExpected)

    def peek_primary_expression(self) -> Node:
        """
        parse a primary expression
        primary_expression
            : IDENTIFIER
            | constant
            | string
            | '(' expression ')'
            ;
        :return: a primary expression node
        """
        if self.is_token_kind(tk.TokenKind.INTEGER_LITERAL):
            number: Number = Number(int(self.current_token.string))
            self.peek_token()  # peek integer literal number
            return number
        elif self.is_token_kind(tk.TokenKind.FLOAT_LITERAL):
            number: Number = Number(float(self.current_token.string))
            self.peek_token()  # peek float literal number
            return number
        elif self.is_token_kind(tk.TokenKind.STRING_LITERAL):
            string_: CString = CString(self.current_token.string)
            self.peek_token()  # peek string literal number
            return string_
        elif self.is_token_kind(tk.TokenKind.IDENTIFIER):
            identifier: CIdentifier = CIdentifier(self.current_token)
            self.peek_token()  # peek identifier literal number
            return identifier
        elif self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek opening parenthesis token

            if not self.is_token_kind(tk.TokenKind.CLOSING_PARENTHESIS):
                expression: Node = self.peek_expression()
                self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expecting a closing parenthesis token",
                                       eh.TokenExpected)
                self.peek_token()  # peek closing parenthesis token
                return expression
            else:
                self.peek_token()  # peek closing parenthesis token
                return NoneNode()
        else:
            self.fatal_token(self.current_token.index, "Expected a primary expression token", eh.PrimaryExpressionNotFound)

    def peek_postfix_expression(self) -> Node:
        """
        parse a postfix expression
        postfix_expression
            : primary_expression
            | postfix_expression '[' expression ']'
            | postfix_expression '(' ')'
            | postfix_expression '(' argument_expression_list ')'
            | postfix_expression '.' IDENTIFIER
            | postfix_expression PTR_OP IDENTIFIER
            | postfix_expression INC_OP
            | postfix_expression DEC_OP
            ;
        :return:
        """
        primary_expression: Node = self.peek_primary_expression()

        if not isinstance(primary_expression, CIdentifier):
            return primary_expression

        if self.is_token_kind(tk.TokenKind.OPENING_BRACKET):
            assert False, "Not implemented"

        elif self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            assert False, "Not implemented"

        elif self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            assert False, "Not implemented"

        elif self.is_token_kind(tk.TokenKind.PTR_OP):
            assert False, "Not implemented"

        elif self.is_token_kind(tk.TokenKind.INC_OP):
            assert False, "Not implemented"

        elif self.is_token_kind(tk.TokenKind.DEC_OP):
            assert False, "Not implemented"

        else:
            raise SyntaxError("Expected a postfix expression token")

    def peek_argument_expression_list(self) -> Node:
        assert False, "Not implemented"

    def peek_unary_expression(self) -> Node:
        """
        parse a unary expression
        unary_expression
            : postfix_expression
            | INC_OP unary_expression
            | DEC_OP unary_expression
            | unary_operator cast_expression
            | SIZEOF unary_expression
            | SIZEOF '(' type_name ')'
            ;
        :return: a unary expression node
        """
        if self.is_token_kind(tk.TokenKind.INC_OP):
            assert False, "Not implemented"
        elif self.is_token_kind(tk.TokenKind.DEC_OP):
            assert False, "Not implemented"
        elif self.is_token_kind(tk.TokenKind.AMPERSAND):
            self.peek_token()  # peek & token

            cast_expression: Node = self.peek_cast_expression()

            return CUnaryOp(CUnaryOpKind.Reference, cast_expression)
        elif self.is_token_kind(tk.TokenKind.ASTERISK):
            self.peek_token()  # peek * token

            cast_expression: Node = self.peek_cast_expression()

            return CUnaryOp(CUnaryOpKind.Dereference, cast_expression)
        elif self.is_token_kind(tk.TokenKind.PLUS):
            self.peek_token()  # peek * token

            cast_expression: Node = self.peek_cast_expression()

            return CUnaryOp(CUnaryOpKind.Plus, cast_expression)
        elif self.is_token_kind(tk.TokenKind.HYPHEN):
            self.peek_token()  # peek - token

            cast_expression: Node = self.peek_cast_expression()

            return CUnaryOp(CUnaryOpKind.Minus, cast_expression)
        elif self.is_token_kind(tk.TokenKind.TILDE):
            self.peek_token()  # peek - token

            cast_expression: Node = self.peek_cast_expression()

            return CUnaryOp(CUnaryOpKind.BitwiseNOT, cast_expression)
        elif self.is_token_kind(tk.TokenKind.EXCLAMATION):
            self.peek_token()  # peek - token

            cast_expression: Node = self.peek_cast_expression()

            return CUnaryOp(CUnaryOpKind.LogicalNOT, cast_expression)
        elif self.is_token_kind(tk.TokenKind.SIZEOF):
            assert False, "Not implemented"

        postfix_expression: Node = self.peek_postfix_expression()

        return postfix_expression

    def peek_cast_expression(self) -> Node:
        if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek ( token

            if self.is_token_type_qualifier() or self.is_token_type_specifier():
                # TODO: need to check if the specifier (of token identifiers) is a typedef in not that should be an unary expression
                type_name: CTypeName = self.peek_type_name()
            else:  # not a cast but a "(" expression ")"
                # we need to drop a token
                self.drop_token()  # drop to the ( token
                unary_expression: Node = self.peek_unary_expression()
                return unary_expression

            self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expecting a closing parenthesis",
                                   eh.TokenExpected)

            self.peek_token()  # peek ) token

            cast_expression: Node = self.peek_cast_expression()

            return CCast(type_name, cast_expression)

        unary_expression: Node = self.peek_unary_expression()

        return unary_expression

    def peek_multiplicative_expression(self) -> Node:
        cast_expression: Node = self.peek_cast_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.ASTERISK):
                self.peek_token()  # peek the * token

                sub_peek_cast_expression: Node = self.peek_cast_expression()

                cast_expression = CBinaryOp(CBinaryOpKind.Multiplication, cast_expression, sub_peek_cast_expression)

            elif self.is_token_kind(tk.TokenKind.SLASH):
                self.peek_token()  # peek the / token

                sub_peek_cast_expression: Node = self.peek_cast_expression()

                cast_expression = CBinaryOp(CBinaryOpKind.Division, cast_expression, sub_peek_cast_expression)

            elif self.is_token_kind(tk.TokenKind.PERCENTAGE):
                self.peek_token()  # peek the % token

                sub_peek_cast_expression: Node = self.peek_cast_expression()

                cast_expression = CBinaryOp(CBinaryOpKind.Modulus, cast_expression, sub_peek_cast_expression)

            else:
                return cast_expression

    def peek_additive_expression(self) -> Node:
        multiplicative_expression: Node = self.peek_multiplicative_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.PLUS):
                self.peek_token()  # peek the + token

                sub_multiplicative_expression: Node = self.peek_multiplicative_expression()

                multiplicative_expression = CBinaryOp(CBinaryOpKind.Addition, multiplicative_expression,
                                                      sub_multiplicative_expression)

            elif self.is_token_kind(tk.TokenKind.HYPHEN):
                self.peek_token()  # peek the - token

                sub_multiplicative_expression: Node = self.peek_multiplicative_expression()

                multiplicative_expression = CBinaryOp(CBinaryOpKind.Subtraction, multiplicative_expression,
                                                      sub_multiplicative_expression)
            else:
                return multiplicative_expression

    def peek_shift_expression(self) -> Node:
        additive_expression: Node = self.peek_additive_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.LEFT_OP):
                self.peek_token()  # peek the << token

                sub_additive_expression: Node = self.peek_additive_expression()

                additive_expression = CBinaryOp(CBinaryOpKind.LeftShift, additive_expression, sub_additive_expression)

            elif self.is_token_kind(tk.TokenKind.RIGHT_OP):
                self.peek_token()  # peek the >> token

                sub_additive_expression: Node = self.peek_additive_expression()

                additive_expression = CBinaryOp(CBinaryOpKind.RightShift, additive_expression, sub_additive_expression)

            else:
                return additive_expression

    def peek_relational_expression(self) -> Node:
        shift_expression: Node = self.peek_shift_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.LESS_THAN):
                self.peek_token()  # peek the < token

                sub_shift_expression: Node = self.peek_shift_expression()

                shift_expression = CBinaryOp(CBinaryOpKind.LessThan, shift_expression, sub_shift_expression)

            elif self.is_token_kind(tk.TokenKind.GREATER_THAN):
                self.peek_token()  # peek the > token

                sub_shift_expression: Node = self.peek_shift_expression()

                shift_expression = CBinaryOp(CBinaryOpKind.GreaterThan, shift_expression, sub_shift_expression)

            elif self.is_token_kind(tk.TokenKind.LE_OP):
                self.peek_token()  # peek the <= token

                sub_shift_expression: Node = self.peek_shift_expression()

                shift_expression = CBinaryOp(CBinaryOpKind.LessThanOrEqualTo, shift_expression, sub_shift_expression)

            elif self.is_token_kind(tk.TokenKind.GE_OP):
                self.peek_token()  # peek the >= token

                sub_shift_expression: Node = self.peek_shift_expression()

                shift_expression = CBinaryOp(CBinaryOpKind.GreaterThanOrEqualTo, shift_expression, sub_shift_expression)

            else:
                return shift_expression

    def peek_equality_expression(self) -> Node:
        relational_expression: Node = self.peek_relational_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.EQ_OP):
                self.peek_token()  # peek the == token

                sub_relational_expression: Node = self.peek_relational_expression()

                relational_expression = CBinaryOp(CBinaryOpKind.EqualTo, relational_expression,
                                                  sub_relational_expression)

            elif self.is_token_kind(tk.TokenKind.NE_OP):
                self.peek_token()  # peek the != token

                sub_relational_expression: Node = self.peek_relational_expression()

                relational_expression = CBinaryOp(CBinaryOpKind.NotEqualTo, relational_expression,
                                                  sub_relational_expression)

            else:
                return relational_expression

    def peek_and_expression(self) -> Node:
        equality_expression: Node = self.peek_equality_expression()

        while self.is_token_kind(tk.TokenKind.AMPERSAND):
            self.peek_token()  # peek the & token

            sub_equality_expression: Node = self.peek_equality_expression()

            equality_expression = CBinaryOp(CBinaryOpKind.BitwiseAND, equality_expression, sub_equality_expression)

        return equality_expression

    def peek_exclusive_or_expression(self) -> Node:
        and_expression: Node = self.peek_and_expression()

        while self.is_token_kind(tk.TokenKind.CIRCUMFLEX):
            self.peek_token()  # peek the ^ token

            sub_and_expression: Node = self.peek_and_expression()

            and_expression = CBinaryOp(CBinaryOpKind.BitwiseXOR, and_expression, sub_and_expression)

        return and_expression

    def peek_inclusive_or_expression(self) -> Node:
        exclusive_or_expression: Node = self.peek_exclusive_or_expression()

        while self.is_token_kind(tk.TokenKind.VERTICAL_BAR):
            self.peek_token()  # peek the | token

            sub_exclusive_or_expression: Node = self.peek_exclusive_or_expression()

            exclusive_or_expression = CBinaryOp(CBinaryOpKind.BitwiseOR, exclusive_or_expression,
                                                sub_exclusive_or_expression)

        return exclusive_or_expression

    def peek_logical_and_expression(self) -> Node:
        inclusive_or_expression: Node = self.peek_inclusive_or_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.AND_OP):
                self.peek_token()  # peek the && token

                sub_inclusive_or_expression: Node = self.peek_inclusive_or_expression()

                inclusive_or_expression = CBinaryOp(CBinaryOpKind.LogicalAND, inclusive_or_expression,
                                                    sub_inclusive_or_expression)
            else:
                return inclusive_or_expression

    def peek_logical_or_expression(self) -> Node:
        logical_and_expression: Node = self.peek_logical_and_expression()

        while self.is_token_kind(tk.TokenKind.OR_OP):
            self.peek_token()  # peek the || token

            sub_logical_and_expression: Node = self.peek_logical_and_expression()

            logical_and_expression = CBinaryOp(CBinaryOpKind.LogicalOR, logical_and_expression,
                                               sub_logical_and_expression)

        return logical_and_expression

    def peek_conditional_expression(self) -> Node:
        logical_or_expression: Node = self.peek_logical_or_expression()

        if self.is_token_kind(tk.TokenKind.QUESTION_MARK):
            self.peek_token()  # peek the ? token

            expression: Node = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.COLON, "Expected ':' in conditional expression", eh.TokenExpected)

            self.peek_token()  # peek the : token 

            conditional_expression: Node = self.peek_conditional_expression()

            return CTernaryOp(logical_or_expression, expression, conditional_expression)

        return logical_or_expression

    def peek_assignment_expression(self) -> Node:
        conditional_expression: Node = self.peek_conditional_expression()

        if self.is_assignment_operator():
            self.peek_token()  # peek assignment operator token

            sub_assignment_expression: Node = self.peek_assignment_expression()

            return CBinaryOp(self.get_binary_assignment_op_kind_(), conditional_expression, sub_assignment_expression)
        else:
            return conditional_expression

    def is_assignment_operator(self) -> bool:
        return self.is_token_kind(tk.TokenKind.EQUALS) or \
               self.is_token_kind(tk.TokenKind.MUL_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.DIV_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.MOD_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.ADD_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.SUB_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.LEFT_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.RIGHT_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.AND_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.XOR_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.OR_ASSIGN)

    def get_binary_assignment_op_kind_(self) -> CBinaryOpKind:
        if self.is_token_kind(tk.TokenKind.EQUALS):
            return CBinaryOpKind.Assignment
        elif self.is_token_kind(tk.TokenKind.MUL_ASSIGN):
            return CBinaryOpKind.MultiplicationAssignment
        elif self.is_token_kind(tk.TokenKind.DIV_ASSIGN):
            return CBinaryOpKind.DivisionAssignment
        elif self.is_token_kind(tk.TokenKind.MOD_ASSIGN):
            return CBinaryOpKind.ModulusAssignment
        elif self.is_token_kind(tk.TokenKind.ADD_ASSIGN):
            return CBinaryOpKind.AdditionAssignment
        elif self.is_token_kind(tk.TokenKind.SUB_ASSIGN):
            return CBinaryOpKind.SubtractionAssignment
        elif self.is_token_kind(tk.TokenKind.LEFT_ASSIGN):
            return CBinaryOpKind.LeftShiftAssignment
        elif self.is_token_kind(tk.TokenKind.RIGHT_ASSIGN):
            return CBinaryOpKind.RightShiftAssignment
        elif self.is_token_kind(tk.TokenKind.AND_ASSIGN):
            return CBinaryOpKind.BitwiseAndAssignment
        elif self.is_token_kind(tk.TokenKind.XOR_ASSIGN):
            return CBinaryOpKind.BitwiseXorAssignment
        elif self.is_token_kind(tk.TokenKind.OR_ASSIGN):
            return CBinaryOpKind.BitwiseOrAssignment
        else:
            raise Exception("Invalid assignment operator token")

    def peek_expression(self) -> Node | list[Node]:
        assignment_expressions: list[Node] = []
        assignment_expression: Node = self.peek_assignment_expression()

        if self.is_token_kind(tk.TokenKind.COMMA):
            assignment_expressions.append(assignment_expression)

        while self.is_token_kind(tk.TokenKind.COMMA):
            self.peek_token()  # peek the , token

            sub_assignment_expression: Node = self.peek_assignment_expression()

            assignment_expressions.append(sub_assignment_expression)

        if len(assignment_expressions) != 0:
            return assignment_expressions
        else:
            return assignment_expression

    def peek_constant_expression(self) -> Node:
        conditional_expression: Node = self.peek_conditional_expression()
        return conditional_expression

    def peek_enumerator(self) -> CEnumMember:
        self.expect_token_kind(tk.TokenKind.IDENTIFIER, "Expecting an identifier", eh.TokenExpected)

        identifier: tk.Token = self.current_token

        enum_member: CEnumMember = CEnumMember(CIdentifier(identifier), NoneNode())

        self.peek_token()  # peek identifier token

        if self.is_token_kind(tk.TokenKind.EQUALS):
            self.peek_token()  # peek the equal token

            member_assigned_value: Node = self.peek_constant_expression()

            enum_member.const_expression = member_assigned_value

        return enum_member

    def peek_enumerator_list(self) -> list[CEnumMember]:
        members: list[CEnumMember] = []

        current_member: CEnumMember = self.peek_enumerator()

        members.append(current_member)

        while self.is_token_kind(tk.TokenKind.COMMA):
            self.peek_token()  # peek comma token

            current_member = self.peek_enumerator()

            members.append(current_member)

            if self.is_token_kind(tk.TokenKind.CLOSING_CURLY_BRACE):
                break

        return members

    def peek_enum_specifier(self) -> CEnum:
        self.expect_token_kind(tk.TokenKind.ENUM, "An enum keyword was expected", SyntaxError)

        self.peek_token()  # peek the enum token

        enum: CEnum = CEnum("", [])

        name: str = ""

        if self.is_token_kind(tk.TokenKind.IDENTIFIER):
            name = self.current_token.string

            self.peek_token()  # peek the identifier token

        members: list[CEnumMember] = []

        if self.is_token_kind(tk.TokenKind.OPENING_CURLY_BRACE):
            self.peek_token()  # peek the opening curly brace token

            members = self.peek_enumerator_list()

            self.expect_token_kind(tk.TokenKind.CLOSING_CURLY_BRACE, "An enumerator list closer is needed", SyntaxError)

            self.peek_token()  # peek the closing curly brace token

        if name == "" and members == []:
            raise SyntaxError("An enum name and/or an enumerator list is needed")

        enum.name = name
        enum.members = members

        return enum

    def parse(self) -> None:
        self.peek_token()

        expression = self.peek_expression()

        """while not (self.current_token is None or self.is_token_kind(tk.TokenKind.END)):
            statement = None

            if self.is_token_kind(tk.TokenKind.ENUM):
                enum: CEnum = self.peek_enum_specifier()
                self.enums.append(enum)
                self.expect_token_kind(tk.TokenKind.SEMICOLON, "A semicolon is needed")
            else:
                self.peek_token()"""
