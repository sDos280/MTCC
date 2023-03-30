import enum
import tmcc_token as tk

class NodeKind(enum.Enum):
    BinaryOperator = enum.Enum()
    # FunctionDeclaration = enum.Enum()
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


class Operator:

    def __init__(self, operation: BinaryOperatorKind, left_operand, right_operand):
        self.operation: BinaryOperatorKind = tk_operation
        self.left_operand = left_operand
        self.right_operand = right_operand

    def __str__(self):
        return f"[operation: {str(self.operation)}, left: {str(self.left_operand)}, right: {str(self.right_operand)}]"


class VariableInitialisation:
    """Variable Initialisation Node"""

    def __init__(self, var: Variable, value):
        self.var: Variable = var
        self.value = value

    def __str__(self):
        return f"[var: {str(self.var)}, value: {str(self.value)}]"
