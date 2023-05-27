from __future__ import annotations
from typing import Union
import enum


class CQualifierKind(enum.Flag):
    Const = enum.auto()
    Volatile = enum.auto()


class CSpecifierKind(enum.IntFlag):
    Void = 1 << 0
    Short = 1 << 2
    Char = 1 << 4
    Int = 1 << 8
    Long = 1 << 10
    Float = 1 << 12
    Double = 1 << 14
    Signed = 1 << 15
    Unsigned = 1 << 16


class CPrimitiveDataTypes(enum.Enum):
    Void = enum.auto()
    Short = enum.auto()
    UShort = enum.auto()
    Char = enum.auto()
    UChar = enum.auto()
    Int = enum.auto()
    UInt = enum.auto()
    Long = enum.auto()
    ULong = enum.auto()
    LongLong = enum.auto()
    ULongLong = enum.auto()
    Float = enum.auto()
    Double = enum.auto()
    LongDouble = enum.auto()

    def __str__(self):
        if self == CPrimitiveDataTypes.Void:
            return "void"
        elif self == CPrimitiveDataTypes.Short:
            return "short"
        elif self == CPrimitiveDataTypes.UShort:
            return "unsigned short"
        elif self == CPrimitiveDataTypes.Char:
            return "char"
        elif self == CPrimitiveDataTypes.UChar:
            return "unsigned char"
        elif self == CPrimitiveDataTypes.Int:
            return "int"
        elif self == CPrimitiveDataTypes.UInt:
            return "unsigned int"
        elif self == CPrimitiveDataTypes.Long:
            return "long"
        elif self == CPrimitiveDataTypes.ULong:
            return "unsigned long"
        elif self == CPrimitiveDataTypes.LongLong:
            return "long long"
        elif self == CPrimitiveDataTypes.ULongLong:
            return "unsigned long long"
        elif self == CPrimitiveDataTypes.Float:
            return "float"
        elif self == CPrimitiveDataTypes.Double:
            return "double"
        elif self == CPrimitiveDataTypes.LongDouble:
            return "long double"


class CStruct:
    pass


class CUnion:
    pass


class CTypedef:
    pass


class CTypeName:
    def __init__(self, is_const: bool, is_volatile: bool, type: CSpecifierType | AbstractType):
        self.is_const: bool = is_const
        self.is_volatile: bool = is_volatile
        self.type: CSpecifierType | AbstractType = type

    def __str__(self):
        str_: str = ""

        if self.is_const:
            str_ += "const "
        if self.is_volatile:
            str_ += "volatile "

        str_ += str(self.type)

        return str_


class CBinaryOpKind(enum.Enum):
    Addition = enum.auto()
    Subtraction = enum.auto()
    Multiplication = enum.auto()
    Division = enum.auto()
    Modulus = enum.auto()
    Assignment = enum.auto()
    EqualTo = enum.auto()
    NotEqualTo = enum.auto()
    GreaterThan = enum.auto()
    LessThan = enum.auto()
    GreaterThanOrEqualTo = enum.auto()
    LessThanOrEqualTo = enum.auto()
    BitwiseAND = enum.auto()
    BitwiseOR = enum.auto()
    BitwiseXOR = enum.auto()
    LeftShift = enum.auto()
    RightShift = enum.auto()
    LogicalAND = enum.auto()
    LogicalOR = enum.auto()
    MultiplicationAssignment = enum.auto()
    DivisionAssignment = enum.auto()
    ModulusAssignment = enum.auto()
    AdditionAssignment = enum.auto()
    SubtractionAssignment = enum.auto()
    LeftShiftAssignment = enum.auto()
    RightShiftAssignment = enum.auto()
    BitwiseAndAssignment = enum.auto()
    BitwiseXorAssignment = enum.auto()
    BitwiseOrAssignment = enum.auto()


class CBinaryOp:
    def __init__(self, kind: CBinaryOpKind, left: Node, right: Node):
        self.kind: CBinaryOpKind = kind
        self.left: Node = left
        self.right: Node = right

    def __str__(self):
        str_: str = "("
        str_ += str(self.left)

        match self.kind:
            case CBinaryOpKind.Addition:
                str_ += ' + '
            case CBinaryOpKind.Subtraction:
                str_ += ' - '
            case CBinaryOpKind.Multiplication:
                str_ += ' * '
            case CBinaryOpKind.Division:
                str_ += ' / '
            case CBinaryOpKind.Modulus:
                str_ += ' % '
            case CBinaryOpKind.Assignment:
                str_ += ' = '
            case CBinaryOpKind.EqualTo:
                str_ += ' == '
            case CBinaryOpKind.NotEqualTo:
                str_ += ' != '
            case CBinaryOpKind.GreaterThan:
                str_ += ' > '
            case CBinaryOpKind.LessThan:
                str_ += ' < '
            case CBinaryOpKind.GreaterThanOrEqualTo:
                str_ += ' >= '
            case CBinaryOpKind.LessThanOrEqualTo:
                str_ += ' <= '
            case CBinaryOpKind.BitwiseAND:
                str_ += ' & '
            case CBinaryOpKind.BitwiseOR:
                str_ += ' | '
            case CBinaryOpKind.BitwiseXOR:
                str_ += ' ^ '
            case CBinaryOpKind.LeftShift:
                str_ += ' << '
            case CBinaryOpKind.RightShift:
                str_ += ' >> '
            case CBinaryOpKind.LogicalAND:
                str_ += ' && '
            case CBinaryOpKind.LogicalOR:
                str_ += ' || '

        str_ += str(self.right)
        str_ += ')'

        return str_


class CUnaryOpKind(enum.Enum):
    """"""
    """
        # https://www.scaler.com/topics/pre-increment-and-post-increment-in-c/
        # increase/increase then return
        PreIncrease = enum.auto()
        PreDecrease = enum.auto()
        # return then increase/increase
        PostIncrease = enum.auto()
        PostDecrease = enum.auto()
    """
    Reference = enum.auto()  # '&'
    Dereference = enum.auto()  # '*'
    Plus = enum.auto()  # '+'
    Minus = enum.auto()  # '-'
    BitwiseNOT = enum.auto()  # '~'
    LogicalNOT = enum.auto()  # '!'


class CUnaryOp:
    def __init__(self, kind: CUnaryOpKind, expression: Node):
        self.kind: CUnaryOpKind = kind
        self.expression: Node = expression

    def __str__(self):
        str_: str = "("

        """         
        case CUnaryOpKind.PreIncrease:
                        str_ += '++'
                        str_ += str(self.expression)
                    case CUnaryOpKind.PreDecrease:
                        str_ += '--'
                        str_ += str(self.expression)
                    case CUnaryOpKind.PostIncrease:
                        str_ += str(self.expression)
                        str_ += '++'
                    case CUnaryOpKind.PostDecrease:
                        str_ += str(self.expression)
                        str_ += '--'
                        """

        match self.kind:
            case CUnaryOpKind.Reference:
                str_ += '&'
            case CUnaryOpKind.Dereference:
                str_ += '*'
            case CUnaryOpKind.Plus:
                str_ += '+'
            case CUnaryOpKind.Minus:
                str_ += '-'
            case CUnaryOpKind.BitwiseNOT:
                str_ += '~'
            case CUnaryOpKind.LogicalNOT:
                str_ += '!'

        str_ += str(self.expression)
        str_ += ')'

        return str_


class CTernaryOp:
    def __init__(self, condition: Node, true_value: Node, false_value: Node):
        self.condition: Node = condition
        self.true_value: Node = true_value
        self.false_value: Node = false_value

    def __str__(self):
        return f"{self.condition} ? {self.true_value} : {self.false_value}"


class CCast:
    def __init__(self, cast_to: CTypeName, cast_expression: Node):
        self.cast_to: CTypeName = cast_to
        self.cast_expression: Node = cast_expression

    def __str__(self):
        return f"({self.cast_to}){self.cast_expression}"


class CEnumMember:
    def __init__(self, name: str, value: Node):
        self.name: str = name
        self.value: Node = value

    def __str__(self) -> str:
        return f"{self.name} = {self.value}"


class CEnum:
    def __init__(self, name: str, members: list[CEnumMember]):
        self.name: str = name
        self.members: list[CEnumMember] = members
        self.current_member_value: int = 0

    def __str__(self):
        member_strings = [str(member) for member in self.members]
        members_str = ",\n".join(member_strings)
        return f"enum {self.name} {{\n{members_str}\n}}"


class Number:

    def __init__(self, value: int | float):
        self.value: int | float = value

    def __str__(self):
        return str(self.value)


class String:
    """String Literal"""

    def __init__(self, contain: str):
        self.contain: str = contain

    def __str__(self):
        return self.contain


class Identifier:
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return self.name


class Variable:
    def __init__(self, name: str, type):
        self.name: str = name
        self.type = type

    def __str__(self):
        return f"{self.type} {self.name};"


class Block:
    def __init__(self):
        self.statements: list[Node] = []
        self.variables: list[Variable] = []  # variables declension list

    def __str__(self):
        return "{" + ";".join(str(s) for s in self.statements) + "}"


class CParameter:
    def __init__(self, name: str, type: CTypeName):
        self.name: str = name
        self.type: CTypeName = type

    def __str__(self):
        return f"{self.type} {self.name}"


class CAbstractArray:
    def __init__(self, size: Node, array_of: AbstractType):
        self.size: Node = size
        self.__array_of: AbstractType = array_of

    def get_child_bottom(self) -> AbstractType:
        try:
            return self.child.get_child_bottom()
        except AttributeError:
            return self.child

    def get_child_bottom_not_none(self) -> AbstractType:
        try:
            return self.child.get_child_bottom_not_none()
        except AttributeError:
            return self.child if self.child is not None else self

    @property
    def child(self) -> AbstractType:
        return self.__array_of

    @child.setter
    def child(self, value: AbstractType):
        self.__array_of = value

    def copy(self):
        return CAbstractArray(self.size, self.__array_of)

    def __str__size(self):
        if isinstance(self.child, CAbstractArray):
            return f"[{self.size}]{self.child.__str__size()}"
        else:
            return f"[{self.size}]"

    def __str__(self):
        if isinstance(self.child, CAbstractArray):
            return f"{self.get_child_bottom()}[{self.size}]{self.child.__str__size()}"
        # elif isinstance(self.child, CAbstractPointer):
        #     return f"{self.child}[{self.size}]"
        else:
            return f"{self.child}[{self.size}]"


class CAbstractPointer:
    def __init__(self, pointer_level: int, pointer_of: AbstractType):
        self.pointer_level: int = pointer_level
        self.__pointer_of: AbstractType = pointer_of

    def get_child_bottom(self) -> AbstractType:
        try:
            return self.child.get_child_bottom()
        except AttributeError:
            return self.child

    def get_child_bottom_not_none(self) -> AbstractType:
        try:
            return self.child.get_child_bottom_not_none()
        except AttributeError:
            return self.child if self.child is not None else self

    @property
    def child(self) -> AbstractType:
        return self.__pointer_of

    @child.setter
    def child(self, value: AbstractType):
        self.__pointer_of = value

    def copy(self):
        return self

    def __str__(self):
        return f"{self.__pointer_of if self.__pointer_of is not None else ''}{'*' * self.pointer_level if not isinstance(self.__pointer_of, CFunction) else ''}"


class CFunction:
    def __init__(self, name: str, parameters: list[CParameter], return_type: CTypeName):
        self.name: str = name
        self.parameters: list[CParameter] = parameters
        self.return_type: CTypeName = return_type

    def __str__(self):
        str_ = f"{self.return_type} "
        str_ += f"{self.name}("
        if len(self.parameters) != 0:
            for parameter in self.parameters:
                str_ += f"{parameter}, "
            str_ = str_[0:-2]

        str_ += ")"

        return str_


class FunctionCall:
    def __init__(self, function: CFunction, parameters_type: list):
        self.function: CFunction = function
        self.parameters_type: list = parameters_type

    def __str__(self):
        str_ = f"{self.function.name}("
        for parameter in self.parameters_type:
            str_ += f"{parameter}, "

        str_ = str_[0:-2]
        str_ += ")"

        return str_


Node = Union[
    Block,
    CEnum,
    CEnumMember,
    Variable,
    Number,
    String,
    Identifier,
    CTernaryOp,
    CBinaryOp,
    CUnaryOp,
    CCast,
    FunctionCall,
    CAbstractPointer,
    CAbstractArray,
    CFunction,
    CAbstractArray,
    CParameter
]
CSpecifierType = Union[CPrimitiveDataTypes, CStruct, CUnion, CEnum, CTypedef]
AbstractType = Union[CFunction, CAbstractPointer, CAbstractArray]
