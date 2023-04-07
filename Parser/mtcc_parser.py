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
    def __init__(self, name: str, return_type: str, arguments: list[Variable]):
        self.name: str = name
        self.return_type: str = return_type
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
        return f"[var: {self.var}]"


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

    def __init__(self, func_dec: FunctionDeclaration, block):
        self.func_dec: FunctionDeclaration = func_dec
        self.block = block

    def __str__(self):
        return f"[func_init: {self.func_dec}, block: {self.block}]"


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

    def peek_type(self) -> Type:
        # for now, we just peek the first token and from that get the type

        if self.peek_token(0).kind == tk.TokenKind.Int:
            return Type(BaseTypeKind.Integer, None)

        if self.peek_token(0).kind == tk.TokenKind.Int:
            return Type(BaseTypeKind.Integer, None)

        assert False, "type not implemented"

    def peek_expression_node(self):
        pass

    def peek_variable_declaration_node(self) -> VariableDeclaration:
        if self.peek_token(0) not in [tk.TokenKind.Int, tk.TokenKind.Float]:
            raise SyntaxError("Type is needed")
        vtype: Type = self.peek_type()
        if self.peek_token(1) != tk.TokenKind.Identifier:
            raise SyntaxError("Identifier is needed")
        vname: tk.Token = self.peek_token(1)

        self.index += 2

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
        while self.peek_token(0).kind != tk.TokenKind.CloseBrace:
            statements.append(self.peek_statement())

        if self.peek_token(0).kind != tk.TokenKind.CloseBrace:
            raise SyntaxError("A closing brace is needed")

        self.index += 1  # the index to the token after the } token

        return Block(statements)

    def peek_function_declaration_or_initialization_node(self) -> FunctionDeclaration | FunctionInitialisation:
        return_type: tk.Token = self.peek_token(0)
        function_name: tk.Token = self.peek_token(1)

        self.index += 3  # move the index to the token after the (

        parameters: list[Variable] = []

        while not (self.peek_token(0).kind == tk.TokenKind.CloseParenthesis or self.peek_token(
                0).kind == tk.TokenKind.EndOfTokens):  # peek the parameters decelerations up to the ) token or EndOfTokens
            parameters.append(self.peek_variable_declaration_node().var)

        if self.peek_token(0).kind != tk.TokenKind.CloseParenthesis:
            raise SyntaxError("A closing parenthesis is needed")

        self.index += 1  # move over the ) token

        if self.peek_token(0).kind == tk.TokenKind.Semicolon:
            self.index += 1
            return FunctionDeclaration(Function(function_name.string,
                                                return_type.string, parameters))
        elif self.peek_token(0).kind == tk.TokenKind.OpenBrace:
            return FunctionInitialisation(Function(function_name.string,
                                                   return_type.string, parameters),
                                          self.peek_block())
        else:
            raise SyntaxError("Wrong token")

    def peek_statement(self) -> FunctionDeclaration:
        if self.peek_token(0).kind in [tk.TokenKind.Int,
                                       tk.TokenKind.Float]:  # have to be an initialization of something
            if self.peek_token(1).kind != tk.TokenKind.Identifier:
                raise SyntaxError("An identifier is needed")
            if self.peek_token(2).kind == tk.TokenKind.OpenParenthesis:  # a function initialization
                return self.peek_function_declaration_or_initialization_node()
            elif self.peek_token(2).kind == tk.TokenKind.Equal:  # a variable initialization
                assert False, "not implemented"
        else:
            self.index += 1

    def parse(self) -> None:
        while self.index < self.tokens_length:
            statement_ = self.peek_statement()
            self.abstract_syntax_tree.append(statement_)
