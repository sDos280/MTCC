import enum
import tmcc_token as tk
import tmcc_lexer as lx


class NodeKind(enum.Enum):
    BinaryOperator = enum.Enum()
    VariableDeclaration = enum.Enum()
    FunctionDeclaration = enum.Enum()
    VariableInitialization = enum.Enum()
    FunctionInitialization = enum.Enum()
    Block = enum.Enum()


class BinaryOperatorKind(enum.Enum):
    Assignment = enum.Enum()
    Addition = enum.Enum()
    Subtraction = enum.Enum()
    Multiplication = enum.Enum()
    Division = enum.Enum()


class Integer:

    def __init__(self, value: int):
        self.value: int = value

    def __str__(self):
        return str(self.value)


class Float:

    def __init__(self, value: float):
        self.value: float = value

    def __str__(self):
        return str(self.value)


class Variable:

    def __init__(self, name: str, vtype: str):
        self.name: str = name
        self.type: str = vtype

    def __str__(self):
        return f"[name: {self.name}, type: {self.type}]"


class Function:
    def __init__(self, name: str, return_type: str, arguments: list[Variable]):
        self.name: str = name
        self.return_type: str = return_type
        self.arguments: list[Variable] = arguments

    def __str__(self):
        str_ = f"[func: {self.name}, return_type: {self.return_type}"
        for argument in range(self.arguments):
            str_ += f", {argument}"
        str_ += "]"
        return str_


class Operator:

    def __init__(self, operation: BinaryOperatorKind, left_operand, right_operand):
        self.operation: BinaryOperatorKind = operation
        self.left_operand = left_operand
        self.right_operand = right_operand

    def __str__(self):
        return f"[operation: {str(self.operation)}, left: {str(self.left_operand)}, right: {str(self.right_operand)}]"


class VariableDeclaration:

    def __init__(self, var: Variable):
        self.var: Variable = var

    def __str__(self):
        return f"[var: {str(self.var)}, value: {str(self.value)}]"


class VariableInitialisation:

    def __init__(self, var_dec: VariableDeclaration, value):
        self.var_dec: Variable = var_dec
        self.value = value

    def __str__(self):
        return f"[var: {str(self.var)}, value: {str(self.value)}]"

class FunctionDeclaration:

    def __init__(self, func: Function):
        self.func: Function = func

    def __str__(self):
        return str(self.func)


class FunctionInitialisation:

    def __init__(self, func_dec: FunctionDeclaration, block):
        self.func_dec: FunctionDeclaration = func_dec
        self.block = block

    def __str__(self):
        return f"[func: {str(self.var)}, block: {str(self.block)}]"


class parser:
    def __init__(self, tokens: list[tk.Token], lexer: lx.lexer):
        self.tokens: list[tk.Token] = tokens
        self.tokens_length: int = len(self.tokens)
        self.lexer: lx.lexer = lexer
        self.index: int = 0  # The current index of the parser in the token.
        self.abstract_syntax_tree = []

    def peek_token(self, offset: int) -> tk.Token:
        return self.tokens[self.index + offset]
    def peek_expression_node(self):
        pass

    def peek_variable_declaration_node(self) -> VariableDeclaration:
        if self.peek_token(0) not in [tk.TokenKind.Int, tk.TokenKind.Float]:
            SyntaxError("Type is needed")
        vtype: tk.Token = self.peek_token(0)
        if self.peek_token(1) != tk.TokenKind.Identifier:
            SyntaxError("Identifier is needed")
        vname: tk.Token = self.peek_token(1)

        self.index += 2

        return VariableDeclaration(Variable(self.lexer.get_token_string(vname), self.lexer.get_token_string(vtype)))

    def peek_variable_initialization_node(self) -> VariableInitialisation:
        var_dec: VariableDeclaration = self.peek_variable_declaration_node()

        if self.peek_token(0) != tk.TokenKind.Equal:
            SyntaxError("Equal sign is needed")

        self.index += 1  # move from the "=" token

        return VariableInitialisation(var_dec, self.peek_expression_node())

    def peek_function_declaration_node(self):
        if self.peek_token(0) not in [tk.TokenKind.Int, tk.TokenKind.Float]:
            SyntaxError("Type is needed")
        return_type: tk.Token = self.peek_token(0)
        if self.peek_token(1) != tk.TokenKind.Identifier:
            SyntaxError("Identifier is needed")
        function_name: tk.Token = self.peek_token(1)

        if self.peek_token(2) != tk.TokenKind.OpenParenthesis:
            SyntaxError("Open Parenthesis sign is needed")

        self.index += 3  # move the index to the token after the (

        if self.peek_token(0).kind != tk.TokenKind.CloseParenthesis:  # no arguments
            return FunctionDeclaration(Function(self.lexer.get_token_string(function_name), self.lexer.get_token_string(return_type)), [])

        arguments = [self.peek_variable_declaration_node()]

        while self.peek_token(0).kind == tk.TokenKind.Comma or self.peek_token(0).kind != tk.TokenKind.CloseParenthesis:
            arguments.append(self.peek_variable_declaration_node())

        return FunctionDeclaration(Function(self.lexer.get_token_string(function_name), self.lexer.get_token_string(return_type)), arguments)

    def peek_function_initialization_node(self):
        return_type: tk.Token = self.peek_token(0)
        function_name: tk.Token = self.peek_token(1)

        self.index += 3  # move the index to the token after the (

        arguments = [self.peek_variable_initialization_node()]

        if self.peek_token(0).kind != tk.TokenKind.CloseParenthesis:  # no arguments
            return Fu

        while self.peek_token(0).kind != tk.TokenKind.Comma or self.peek_token(0).kind != tk.TokenKind.CloseParenthesis:
            arguments.append(self.peek_variable_initialization_node())

    def peek_node(self):
        if self.peek_token(0).kind in [tk.TokenKind.Int, tk.TokenKind.Float]:  # have to be an initialization of something
            if self.peek_token(1).kind != tk.TokenKind.Identifier:
                SyntaxError("An identifier is needed")

            if self.peek_token(2).kind == tk.TokenKind.OpenParenthesis:  # a function initialization
                self.peek_function_initialization_node()
            elif self.peek_token(2).kind in tk.TokenKind.Equal:  # a variable initialization
                pass
        else:
            self.index += 1

    def parse(self) -> None:
        while self.index < self.tokens_length:
            self.abstract_syntax_tree.append(self.peek_node())
