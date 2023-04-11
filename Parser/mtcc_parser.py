from __future__ import annotations

import enum

import Parser.mtcc_token as tk
from typing import Union


class BaseType(enum.Enum):
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


EnumTypeDec = EnumType  # enum type declaration

Type = Union[BaseType, EnumType]


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
    def __init__(self, tokens: list[tk.Token]):
        self.tokens: list[tk.Token] = tokens
        self.current_token: tk.Token = None
        self.index: int = -1
        self.AST: list[Statement] = []

        self.enums: list[EnumTypeDec] = []
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

    def is_type_name_declared(self, name: str):
        for enum in self.enums:
            if name == enum.name:
                return True

        """for struct in self.structs:
            if name == struct.name:
                return True"""

        return False

    def is_enum_member_name_declared(self, name: str):
        for enum in self.enums:
            for member in enum.members:
                if name == member.name:
                    return True
        return False

    def peek_token(self) -> None:  # increase the index and update the current token
        self.index += 1
        self.current_token = self.tokens[self.index]

    def drop_token(self) -> None:  # decrease the index and update the current token
        self.index -= 1
        self.current_token = self.tokens[self.index]

    def peek_enum_declaration_member(self, enum_dec: EnumTypeDec) -> EnumMember:
        member: EnumMember = EnumMember("", enum_dec.current_member_value)

        if self.current_token.kind != tk.TokenKind.Identifier:
            raise SyntaxError("An enum member name is needed")

        if self.is_enum_member_name_declared(self.current_token.string):
            raise SyntaxError("The name of enum member is already taken")

        member.name = self.current_token.string

        self.peek_token()  # peek enum member name token

        if self.current_token.kind == tk.TokenKind.Equal:
            self.peek_token()  # peek equal sign token

            if self.current_token.kind != tk.TokenKind.IntegerLiteral:
                raise SyntaxError("An integer literal is needed")

            member.value = int(self.current_token.string)
            enum_dec.current_member_value = int(self.current_token.string)

            self.peek_token()  # peek the integer literal token

        enum_dec.current_member_value += 1  # increase the current member value of the enum

        return member

    def peek_enum_declaration_block(self, enum_dec: EnumTypeDec) -> list[EnumMember]:
        members: list[EnumMember] = []

        if self.current_token.kind != tk.TokenKind.OpenBrace:
            raise SyntaxError("An enum block opener is needed: \'{\'")

        self.peek_token()  # peek the { token

        while self.current_token.kind != tk.TokenKind.CloseBrace:
            if self.current_token.kind == tk.TokenKind.EndOfTokens:
                raise SyntaxError("An enum block closer is needed: \'}\'")

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
            if self.is_type_name_declared(self.current_token.string):
                raise SyntaxError("The name of enum is already taken")
            enum_dec.name = self.current_token.string

            self.peek_token()  # peek the name token

        if self.current_token.kind == tk.TokenKind.OpenBrace:
            enum_dec.members = self.peek_enum_declaration_block(enum_dec)
        else:
            raise SyntaxError("An enum block opener is needed: \'{\'")

        self.peek_token()  # peek the } token

        return enum_dec

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
            else:
                self.peek_token()

            if statement is not None:
                self.AST.append(statement)

        print("sdgdfgfdg")