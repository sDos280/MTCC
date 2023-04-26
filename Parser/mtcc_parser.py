from __future__ import annotations

from typing import Union, Type, List
from enum import Enum

import Parser.mtcc_token as tk


class CLogicalOrExpression:
    def __init__(self, expression_left, expression_right):
        self.expression_left = expression_left
        self.expression_right = expression_right

    def __str__(self):
        return f"{self.expression_left} || {self.expression_right}"


class CConditionalExpression:
    def __init__(self, condition, true_value, false_value):
        self.condition = condition
        self.true_value = true_value
        self.false_value = false_value

    def __str__(self):
        return f"{self.condition} ? {self.true_value} : {self.false_value}"


class CBasicType(Enum):
    CHAR = 'char'
    SIGNED_CHAR = 'signed char'
    UNSIGNED_CHAR = 'unsigned char'
    SHORT = 'short'
    UNSIGNED_SHORT = 'unsigned short'
    INT = 'int'
    UNSIGNED_INT = 'unsigned int'
    LONG = 'long'
    UNSIGNED_LONG = 'unsigned long'
    LONG_LONG = 'long long'
    UNSIGNED_LONG_LONG = 'unsigned long long'
    FLOAT = 'float'
    DOUBLE = 'double'
    LONG_DOUBLE = 'long double'


class TypeQualifier(Enum):
    CONST = 'const'
    VOLATILE = 'volatile'
    RESTRICT = 'restrict'


class CQualifiedType:
    def __init__(self, base_type: CBasicType, qualifiers: list[TypeQualifier]):
        self.base_type = base_type
        self.qualifiers = qualifiers

    def __str__(self) -> str:
        base_str = self.base_type.value
        qual_str = " ".join(q.value for q in self.qualifiers)

        return f"{qual_str} {base_str}"


class CEnumMember:
    def __init__(self, name: str, value: int):
        self.name: str = name
        self.value: int = value

    def __str__(self) -> str:
        return f"{self.name} = {self.value}"


class CEnum:
    def __init__(self, name: str, members: List[CEnumMember]):
        self.name: str = name
        self.members: List[CEnumMember] = members
        self.current_member_value: int = 0

    def __str__(self):
        member_strings = [str(member) for member in self.members]
        members_str = ",\n".join(member_strings)
        return f"enum {self.name} {{\n{members_str}\n}}"


class Variable:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return f"{self.type} {self.name};"


class Block:
    def __init__(self):
        self.statements = []

    def add_statement(self, statement):
        self.statements.append(statement)

    def __str__(self):
        return "{" + "\n".join(str(s) for s in self.statements) + "}"


Node = Union[Block, Variable, CEnum, CEnumMember, CQualifiedType, CConditionalExpression]


class Parser:
    def __init__(self, tokens: list[tk.Token]):
        self.tokens: list[tk.Token] = tokens
        self.current_token: tk.Token = None
        self.index: int = -1
        self.AST: list = []

        self.enums: list[CEnum] = []

    def peek_token(self) -> None:  # increase the index and update the current token
        self.index += 1
        self.current_token = self.tokens[self.index]

    def drop_token(self) -> None:  # decrease the index and update the current token
        self.index -= 1
        self.current_token = self.tokens[self.index]

    def is_variable_in_block(self):
        pass

    def expect_token_kind(self, token_kind: tk.TokenKind, error: str) -> None:
        if self.current_token.kind != token_kind:
            raise SyntaxError(error)

    def dont_expect_token_kind(self, token_kind: tk.TokenKind, error: str) -> None:
        if self.current_token.kind == token_kind:
            raise SyntaxError(error)

    def is_token_kind(self, token_kind: tk.TokenKind) -> bool:
        return self.current_token.kind == token_kind

    def peek_logical_or_expression(self):
        logical_and_expression = self.peek_logical_and_expression()

        if self.is_token_kind(tk.TokenKind.OR_OP):
            self.peek_token()  # peek the or operator token

            logical_and_expression = self.peek_logical_and_expression()

        return logical_and_expression

    def peek_conditional_expression(self):
        logical_or_expression = self.peek_logical_or_expression()

        if self.is_token_kind(tk.TokenKind.QUESTION_MARK):
            self.peek_token()  # peek question mark token

            expression = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.COLON, 'Expecting a colon')

            self.peek_token()  # peek colon token

            conditional_expression = self.peek_conditional_expression()

            return CConditionalExpression(logical_or_expression, expression, conditional_expression)

        return logical_or_expression

    def peek_constant_expression(self):
        node = self.peek_conditional_expression()
        return node

    def peek_enumerator(self, enum: CEnum) -> CEnumMember:
        self.expect_token_kind(tk.TokenKind.Identifier, "Expecting an identifier")

        enum.current_member_value += 1
        name: str = self.current_token.string

        self.peek_token()  # peek identifier token

        member: CEnumMember = CEnumMember(name, enum.current_member_value)

        if self.is_token_kind(tk.TokenKind.EQUALS):
            self.peek_token()  # peek the equal token

            member_assigned_value: int = self.peek_constant_expression()

            member.value = member_assigned_value
            enum.current_member_value = member_assigned_value

        return member

    def peek_enumerator_list(self, enum: CEnum) -> list[CEnumMember]:
        members: list[CEnumMember] = []

        current_member: CEnumMember = self.peek_enumerator(enum)

        members.append(current_member)

        while self.is_token_kind(tk.TokenKind.COMMA):
            self.peek_token()  # peek comma token

            current_member = self.peek_enumerator(enum)

            members.append(current_member)

            self.dont_expect_token_kind(tk.TokenKind.END, "Expecting an identifier or an close brace")

            if self.is_token_kind(tk.TokenKind.CLOSING_CURLY_BRACE):
                break

        return members

    def peek_enum_specifier(self) -> CEnum:
        self.expect_token_kind(tk.TokenKind.ENUM, "An enum keyword was expected")

        self.peek_token()  # peek the enum token

        enum: CEnum = CEnum("", [])

        name: str = ""

        if self.is_token_kind(tk.TokenKind.Identifier):
            name = self.current_token.string

            self.peek_token()  # peek the identifier token

        members: list[CEnumMember] = []

        if self.is_token_kind(tk.TokenKind.OPENING_CURLY_BRACE):
            self.peek_token()  # open the opening curly brace token

            members = self.peek_enumerator_list(enum)

            self.expect_token_kind(tk.TokenKind.CLOSING_CURLY_BRACE, "An enumerator list closer is needed")

            self.peek_token()  # peek the closing curly brace token

        if name == "" and members == []:
            raise SyntaxError("An enum name and/or an enumerator list is needed")

        enum.name = name
        enum.members = members

        return enum

    def parse(self) -> None:
        self.peek_token()

        while not (self.current_token is None or self.current_token.kind == tk.TokenKind.END):
            statement = None

            if self.current_token.kind == tk.TokenKind.ENUM:
                enum = self.peek_enum_specifier()
                self.enums.append(enum)
                self.expect_token_kind(tk.TokenKind.SEMICOLON, "A semicolon is needed")
            else:
                self.peek_token()

            if statement is not None:
                self.AST.append(statement)
