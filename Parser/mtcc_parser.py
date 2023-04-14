from __future__ import annotations

import enum

import Parser.mtcc_token as tk
import Parser.mtcc_error_handler as eh
from typing import Union


class BasicTypeKind(enum.Enum):
    Integer = enum.auto()
    Float = enum.auto()

    def __str__(self):
        return f"{self.name}"


class EnumMember:
    def __init__(self, name: str, value: int):
        self.name: str = name
        self.value: int = value

    def __str__(self):
        return f"{self.name}: {self.value}"


class EnumType:
    def __init__(self, name: str, members: list[EnumMember]):
        self.name: str = name
        self.members: list[EnumMember] = members
        self.current_member_value: int = 0  # used when parsing

    def __str__(self):
        str_ = f"enum_name: {self.name}, members: ["

        if len(self.members) != 0:
            for member in self.members:
                str_ += f"{member}, "

            str_ = str_[0:-2]

        str_ += "]"

        return str_


class PointerType:
    def __init__(self, contain: Type, level: int, is_contain_const: bool):
        self.contain: Type = contain
        self.level: int = level  # the pointer level
        self.is_contain_const: bool = is_contain_const

    def __str__(self):
        return f"contain: [{self.contain}], level: {self.level}, contain_const: {self.is_contain_const}"


class BaseType:

    def __init__(self, kind: BasicTypeKind, is_const: bool):
        self.kind: BasicTypeKind = kind
        self.is_const: bool = is_const

    def __str__(self):
        return f"kind: {self.kind}, const: {self.is_const}"


class Typedef:
    def __init__(self, name: str, type: Type):
        self.type: Type = type
        self.name: str = name

    def __str__(self):
        return f"name: {self.name}, type: [{self.type}]"


EnumTypeDec = EnumType  # enum type declaration
TypedefDec = Typedef  # typedef declaration
Type = Union[BasicTypeKind, EnumType, PointerType, BaseType]


class Variable:
    def __init__(self, name: str, type: Type):
        self.name: str = name
        self.type: Type = type

    def __str__(self):
        return f"var_name: {self.name}, var_type: {self.type}"


class Block:

    def __init__(self, statements: list[Statement], local_vars: list[Variable]):
        self.statements: list[Statement] = statements

        self.local_vars: list[Variable] = local_vars

    def __str__(self):
        str_ = "["
        for statement in self.statements:
            str_ += f"{statement}, "

        str_ = str_[0:-2]
        return str_


Statement = Union[Block, EnumTypeDec]


class Parser:
    def __init__(self, tokens: list[tk.Token], error_handler: eh.ErrorHandler):
        self.tokens: list[tk.Token] = tokens
        self.current_token: tk.Token = None
        self.error_handler: eh.ErrorHandler = error_handler
        self.index: int = -1
        self.AST: list[Statement] = []

        self.enums: list[EnumTypeDec] = []
        self.typedefs: list[TypedefDec] = []
        self.local_vars: list[Variable] = []

    def is_var_name_declared(self, name: str, block: Block) -> bool:
        if block is None:  # we are looking on the toplevel block
            for var in self.local_vars:
                if name == var.name:
                    return True
            return False
        else:
            for var in block.local_vars:
                if name == var.name:
                    return True
            return False

    def is_enum_member_name_declared(self, name: str):
        for enum in self.enums:
            for member in enum.members:
                if name == member.name:
                    return True
        return False

    def is_enum_name_declared(self, name: str):
        for enum in self.enums:
            if name == enum.name:
                return True

        return False

    def is_typedef_name_declared(self, name: str):
        for typedef in self.typedefs:
            if name == typedef.name:
                return True

        return False

    def peek_token(self) -> None:  # increase the index and update the current token
        self.index += 1
        self.current_token = self.tokens[self.index]

    def drop_token(self) -> None:  # decrease the index and update the current token
        self.index -= 1
        self.current_token = self.tokens[self.index]

    def expect_token(self, expected_token: tk.TokenKind, expected_token_string: str, error_string: str):
        if self.current_token.kind != expected_token:
            self.drop_token()  # we drop a token to get the before token
            self.error_handler.expect_token_syntax_error(self.current_token, expected_token_string, error_string)

    def dont_expect_token(self, expected_token: tk.TokenKind, expected_token_string: str, error_string: str):
        if self.current_token.kind == expected_token:
            self.drop_token()  # we drop a token to get the before token
            self.error_handler.expect_token_syntax_error(self.current_token, expected_token_string, error_string)


    def peek_pointer_type_attributes(self) -> PointerType:
        pointer_level: int = 0

        self.expect_token(tk.TokenKind.Asterisk, '*', "An asterisk is needed")

        self.peek_token()  # peek the asterisk token

        pointer_level += 1

        while self.current_token.kind == tk.TokenKind.Asterisk:
            self.peek_token()  # peek the asterisk token

            pointer_level += 1

        contain_const: bool = False

        if self.current_token.kind == tk.TokenKind.Const:
            contain_const = True

            self.peek_token()  # peek the const type

        pointer_type = PointerType(None, pointer_level, contain_const)

        return pointer_type

    def peek_type(self) -> Type:
        is_const: bool = False
        if self.current_token.kind == tk.TokenKind.Const:
            is_const = True
            self.peek_token()  # peek the const token

        base_type_kind: BasicTypeKind = None
        if self.current_token.kind == tk.TokenKind.Int:
            base_type_kind = BasicTypeKind.Integer
            self.peek_token()  # peek the int token
        elif self.current_token.kind == tk.TokenKind.Float:
            base_type_kind = BasicTypeKind.Float
            self.peek_token()  # peek the float token

        if base_type_kind is not None:
            base_type = BaseType(base_type_kind, is_const)

            if self.current_token.kind == tk.TokenKind.Asterisk:  # may be a pointer
                pointer_type: PointerType = self.peek_pointer_type_attributes()

                pointer_type.contain = base_type

                return pointer_type

            return base_type

        assert False, "not implemented"

    def peek_enum_declaration_member(self, enum_dec: EnumTypeDec) -> EnumMember:
        member: EnumMember = EnumMember("", enum_dec.current_member_value)

        self.expect_token(tk.TokenKind.Identifier, '', "An enum member name is needed")

        if self.is_enum_member_name_declared(self.current_token.string):
            raise SyntaxError("The name of enum member is already taken")

        member.name = self.current_token.string

        self.peek_token()  # peek enum member name token

        if self.current_token.kind == tk.TokenKind.Equal:
            self.peek_token()  # peek equal sign token

            self.expect_token(tk.TokenKind.IntegerLiteral, '', "An integer literal is needed")

            member.value = int(self.current_token.string)
            enum_dec.current_member_value = int(self.current_token.string)

            self.peek_token()  # peek the integer literal token

        enum_dec.current_member_value += 1  # increase the current member value of the enum

        return member

    def peek_enum_declaration_block(self, enum_dec: EnumTypeDec) -> list[EnumMember]:
        members: list[EnumMember] = []

        self.expect_token(tk.TokenKind.OpenBrace, '{', "An enum block opener is needed: \'{\'")

        self.peek_token()  # peek the { token

        while self.current_token.kind != tk.TokenKind.CloseBrace:
            self.dont_expect_token(tk.TokenKind.EndOfTokens, '}', "An enum block closer is needed")

            member: EnumMember = self.peek_enum_declaration_member(enum_dec)

            members.append(member)

            if self.current_token.kind not in [tk.TokenKind.Comma, tk.TokenKind.CloseBrace, tk.TokenKind.EndOfTokens]:
                raise SyntaxError("An enum member seperator or an enum block closer is needed: \',\' | \'}\'")

            if self.current_token.kind == tk.TokenKind.EndOfTokens:
                raise SyntaxError("An enum block closer is needed: \'}\'")

            if self.current_token.kind == tk.TokenKind.CloseBrace:
                break

            self.peek_token()  # peek the , token

        return members

    def peek_enum_declaration(self) -> EnumTypeDec:
        enum_dec = EnumTypeDec("", [])

        if self.current_token.kind != tk.TokenKind.Enum:
            raise SyntaxError("An enum keyword is needed")

        self.peek_token()  # peek the enum token

        if self.current_token.kind == tk.TokenKind.Identifier:
            if self.is_enum_name_declared(self.current_token.string):
                raise SyntaxError("The name of enum is already taken")
            enum_dec.name = self.current_token.string

            self.peek_token()  # peek the name token

        if self.current_token.kind == tk.TokenKind.OpenBrace:
            enum_dec.members = self.peek_enum_declaration_block(enum_dec)
        else:
            self.expect_token(tk.TokenKind.OpenBrace, '{', "An enum block opener is needed")

        self.peek_token()  # peek the } token

        return enum_dec

    def peek_typedef_declaration(self) -> TypedefDec:
        self.expect_token(tk.TokenKind.Typedef, "typedef", "A typedef keyword is needed")

        self.peek_token()  # peek the typedef token

        type: BaseType = self.peek_type()

        self.expect_token(tk.TokenKind.Identifier, '', "An identifier is needed")

        if self.is_typedef_name_declared(self.current_token.string):
            raise SyntaxError("The typedef name is already declared")

        name: str = self.current_token.string

        self.peek_token()  # peek the identifier token

        typedef: TypedefDec = TypedefDec(name, type)

        return typedef

    def peek_statement(self) -> Statement:
        if self.current_token.kind == tk.TokenKind.Enum:
            pass
        else:
            self.peek_token()

    def parse(self) -> None:
        self.peek_token()

        while not (self.current_token is None or self.current_token.kind == tk.TokenKind.EndOfTokens):
            statement: Statement = None

            if self.current_token.kind == tk.TokenKind.Enum:
                enum: EnumTypeDec = self.peek_enum_declaration()
                self.enums.append(enum)
                self.expect_token(tk.TokenKind.Semicolon, ';', "A semicolon is needed")
            elif self.current_token.kind == tk.TokenKind.Typedef:
                typedef: TypedefDec = self.peek_typedef_declaration()
                self.typedefs.append(typedef)
                self.expect_token(tk.TokenKind.Semicolon, ';', "A semicolon is needed")
            else:
                self.peek_token()

            if statement is not None:
                self.AST.append(statement)
