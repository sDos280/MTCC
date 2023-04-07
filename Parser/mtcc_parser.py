from __future__ import annotations
from typing import Union
import enum
import Parser.mtcc_token as tk
import Parser.mtcc_lexer as lx


class BinaryOperatorKind(enum.Enum):
    Assignment = enum.auto()
    Addition = enum.auto()
    Subtraction = enum.auto()
    Multiplication = enum.auto()
    Division = enum.auto()


class BaseTypeKind(enum.Enum):
    Integer = enum.auto()
    Float = enum.auto()
    Array = enum.auto()
    Pointer = enum.auto()
    Struct = enum.auto()


class Type:
    def __init__(self, base_type_kind: BaseTypeKind, base_type: Type | str | None):
        self.base_type_kind: BaseTypeKind = base_type_kind
        self.base_type: Type | str = base_type  # str for struct (the name of the struct) and None for Integer/Float

    def __str__(self):
        str_ = ""
        match self.base_type_kind:
            case BaseTypeKind.Integer:
                str_ = "int"
            case BaseTypeKind.Float:
                str_ = "float"
            case BaseTypeKind.Array:
                str_ = f"array: {self.base_type}"
            case BaseTypeKind.Pointer:
                str_ = f"pointer: {self.base_type}"
            case BaseTypeKind.Struct:
                str_ = f"struct: {self.base_type}"

        return str_


class Variable:

    def __init__(self, name: str, vtype: Type):
        self.name: str = name
        self.type: Type = vtype

    def __str__(self):
        return f"[name: {self.name}, type: {self.type}]"


class Function:
    def __init__(self, name: str, return_type: Type, arguments: list[Variable]):
        self.name: str = name
        self.return_type: Type = return_type
        self.arguments: list[Variable] = arguments

    def __str__(self):
        str_ = f"[func: {self.name}, return_type: {self.return_type}"
        for argument in range(len(self.arguments)):
            str_ += f", {argument}"
        str_ += "]"
        return str_


class Operator:

    def __init__(self, operation: BinaryOperatorKind, left_operand, right_operand):
        self.operation: BinaryOperatorKind = operation
        self.left_operand = left_operand
        self.right_operand = right_operand

    def __str__(self):
        return f"[operation: {self.operation}, left: {self.left_operand}, right: {self.right_operand}]"


mtcc_exception = Union[Variable, Operator]


class VariableDeclaration:

    def __init__(self, var: Variable):
        self.var: Variable = var

    def __str__(self):
        return f"[var_dec: {self.var}]"


class VariableInitialisation:

    def __init__(self, var: Variable, value):
        self.var: Variable = var
        self.value = value

    def __str__(self):
        return f"[var_init: {self.var}, value: {self.value}]"


class FunctionDeclaration:

    def __init__(self, func: Function):
        self.func: Function = func

    def __str__(self):
        str_ = f"[func_dec: {self.func.name}, return_type: {self.func.return_type}"
        for argument in range(len(self.func.arguments)):
            str_ += f", {argument}"
        str_ += "]"
        return str_


class FunctionInitialisation:

    def __init__(self, func: Function, block):
        self.func: Function = func
        self.block = block

    def __str__(self):
        return f"[func_init: {self.func}, block: {self.block}]"


class Block:

    def __init__(self, statements: list):
        self.statements = statements
        self.local_variables: list[Variable] = []

    def __str__(self):
        str_ = "["
        if len(self.statements) == 0:
            return str_ + "]"
        elif len(self.statements) == 1:
            str_ += str(self.statements[0]) + "]"
            return str_

        for statement in self.statements:
            str_ += str(statement) + ", "

        str_ = str_[0: -2]
        str_ += "]"

        return str_


class Parser:
    def __init__(self, tokens: list[tk.Token], lexer: lx.lexer):
        self.tokens: list[tk.Token] = tokens
        self.tokens_length: int = len(self.tokens)
        self.lexer: lx.lexer = lexer
        self.index: int = 0  # The current index of the parser in the token.
        self.abstract_syntax_tree = []

    def peek_token(self, offset: int) -> tk.Token:
        return self.tokens[self.index + offset]

    def bump(self, by: int) -> None:
        self.index += by

    def peek_identifier(self):
        token: tk.Token = self.peek_token(0)

        if token.kind != tk.TokenKind.Identifier:
            raise SyntaxError("An identifier is needed")

        self.bump(1)

        return token

    def peek_type(self) -> Type:
        # for now, we just peek the first token and from that get the type

        token: tk.Token = self.peek_token(0)

        self.bump(1)

        if token.kind == tk.TokenKind.Int:
            return Type(BaseTypeKind.Integer, None)

        elif token.kind == tk.TokenKind.Float:
            return Type(BaseTypeKind.Float, None)
        else:
            assert False, "type not implemented"

    def peek_expression_node(self):
        pass

    def peek_variable_declaration(self) -> VariableDeclaration:
        vtype: Type = self.peek_type()
        vname: tk.Token = self.peek_identifier()

        self.bump(1)

        return VariableDeclaration(
            Variable(vname.string, vtype))

    """def peek_variable_initialization_node(self) -> VariableInitialisation:
        var_dec: VariableDeclaration = self.peek_variable_declaration_node()

        if self.peek_token(0) != tk.TokenKind.Equal:
            SyntaxError("Equal sign is needed")

        self.index += 1  # move from the "=" token

        return VariableInitialisation(var_dec, self.peek_expression_node())"""

    def peek_block(self) -> Block:
        statements = []
        while not (self.peek_token(0).kind == tk.TokenKind.CloseBrace or self.peek_token(
                0).kind == tk.TokenKind.EndOfTokens):
            statements.append(self.peek_statement())

        if self.peek_token(0).kind != tk.TokenKind.CloseBrace:
            raise SyntaxError("A closing brace is needed")

        self.bump(1)  # the index to the token after the } token

        return Block(statements)

    def peek_function_declaration_or_initialization(self) -> FunctionDeclaration | FunctionInitialisation:
        return_type: Type = self.peek_type()
        function_name: tk.Token = self.peek_identifier()

        self.bump(1)  # move the index to the token after the (

        parameters: list[Variable] = []

        while not (self.peek_token(0).kind == tk.TokenKind.CloseParenthesis or
                   self.peek_token(
                       0).kind == tk.TokenKind.EndOfTokens):  # peek the parameters decelerations up to the ) token or EndOfTokens
            parameters.append(self.peek_variable_declaration().var)

        if self.peek_token(0).kind != tk.TokenKind.CloseParenthesis:
            raise SyntaxError("A closing parenthesis is needed")

        self.bump(1)  # move over the ) token

        if self.peek_token(0).kind == tk.TokenKind.Semicolon:
            self.bump(1)
            return FunctionDeclaration(Function(function_name.string,
                                                return_type, parameters))
        elif self.peek_token(0).kind == tk.TokenKind.OpenBrace:
            self.bump(1)
            return FunctionInitialisation(Function(function_name.string,
                                                   return_type, parameters),
                                          self.peek_block())
        else:
            raise SyntaxError("Wrong token")

    def peek_statement(self) -> FunctionDeclaration | FunctionInitialisation | VariableDeclaration:
        if self.peek_token(0).kind in [tk.TokenKind.Int,
                                       tk.TokenKind.Float]:  # have to be an initialization of something
            if self.peek_token(1).kind != tk.TokenKind.Identifier:
                raise SyntaxError("An identifier is needed")
            if self.peek_token(2).kind == tk.TokenKind.OpenParenthesis:  # a function initialization or declension
                return self.peek_function_declaration_or_initialization()
            elif self.peek_token(2).kind == tk.TokenKind.Equal or self.peek_token(
                    2).kind == tk.TokenKind.Semicolon:  # a variable initialization
                return self.peek_variable_declaration()
        else:
            self.bump(1)

    def parse(self) -> None:
        while self.index < self.tokens_length and self.peek_token(0).kind != tk.TokenKind.EndOfTokens:
            statement_ = self.peek_statement()
            self.abstract_syntax_tree.append(statement_)
