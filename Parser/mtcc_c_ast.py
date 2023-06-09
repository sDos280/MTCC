from __future__ import annotations
from typing import Union
import enum
import Parser.mtcc_token as tk


class CQualifierKind(enum.IntFlag):
    Const = enum.auto()
    Volatile = enum.auto()

    def to_dict(self):
        return {
            "node": "CQualifierKind",
            "value": str(self)
        }


class CStorageClassSpecifier(enum.IntFlag):
    Typedef = enum.auto()
    Extern = enum.auto()
    Static = enum.auto()
    Auto = enum.auto()
    Register = enum.auto()


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

    def to_dict(self):
        return {
            "node": "CPrimitiveDataTypes",
            "value": str(self)
        }


class NoneNode:
    def to_dict(self):
        return ''


class CStruct:
    pass


class CUnion:
    pass


class CTypedef:
    def __init__(self, name: CIdentifier, type_name: CTypeName):
        self.name: CIdentifier = name
        self.type_name: CTypeName = type_name

    def to_dict(self):
        return {
            "node": "CTypedef",
            "name": self.name.to_dict(),
            "type_name": self.type_name.to_dict()
        }


class CTypeName:
    def __init__(self, type: CSpecifierType | CType):
        self.type: CSpecifierType | CType = type

    def to_dict(self):
        return {
            "node": "CTypeName",
            "type": self.type.to_dict()
        }


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

    def to_dict(self):
        return {
            "node": "CBinaryOp",
            "kind": self.kind.name,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


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

    def to_dict(self):
        return {
            "node": "CUnaryOp",
            "kind": self.kind.name,
            "expression": self.expression.to_dict()
        }


class CTernaryOp:
    def __init__(self, condition: Node, true_value: Node, false_value: Node):
        self.condition: Node = condition
        self.true_value: Node = true_value
        self.false_value: Node = false_value

    def to_dict(self):
        return {
            "node": "CTernaryOp",
            "condition": self.condition.to_dict(),
            "true_value": self.true_value.to_dict(),
            "false_value": self.false_value.to_dict()
        }


class CCast:
    def __init__(self, cast_to: CTypeName, cast_expression: Node):
        self.cast_to: CTypeName = cast_to
        self.cast_expression: Node = cast_expression

    def to_dict(self):
        return {
            "node": "CCast",
            "cast_to": self.cast_to.to_dict(),
            "cast_expression": self.cast_expression.to_dict()
        }


class CEnumMember:
    def __init__(self, identifier: CIdentifier | NoneNode, const_expression: Node):
        self.identifier: CIdentifier | NoneNode = identifier
        self.const_expression: Node = const_expression

    def to_dict(self):
        return {
            "node": "CEnumMember",
            "name": str(self.identifier) if not isinstance(self.identifier, NoneNode) else self.identifier.to_dict(),
            "value": self.const_expression.to_dict()
        }


class CEnum:
    def __init__(self, name: str, members: list[CEnumMember]):
        self.name: str = name
        self.members: list[CEnumMember] = members
        self.current_member_value: Node = Number(0)

    def to_dict(self):
        return {
            "node": "CEnum",
            "name": self.name,
            "members": [member.to_dict() for member in self.members]
        }


class Number:
    def __init__(self, value: int | float):
        self.value: int | float = value

    def to_dict(self):
        return {
            "node": "Number",
            "value": self.value
        }


class CString:

    def __init__(self, contain: str):
        self.contain: str = contain

    def to_dict(self):
        return {
            "node": "CString",
            "contain": self.contain
        }


class CIdentifier:
    def __init__(self, token: tk.Token | None):
        self.token: tk.Token | None = token

    def to_dict(self):
        return {
            "node": "CIdentifier",
            "token": self.token.string
        } if self.token is not None else {
            "node": "CIdentifier",
            "token": ""
        }

    def __str__(self):
        return self.token.string if self.token is not None else ""


class Variable:
    def __init__(self, identifier: CIdentifier | NoneNode, type):
        self.identifier: CIdentifier | NoneNode = identifier
        self.type = type

    def to_dict(self):
        return {
            "node": "Variable",
            "name": str(self.identifier) if not isinstance(self.identifier, NoneNode) else self.identifier.to_dict(),
            "type": self.type.to_dict()
        }


class Block:
    def __init__(self):
        self.statements: list[Node] = []
        self.variables: list[Variable] = []  # variables declension list

    def to_dict(self):
        return {
            "node": "Block",
            "statements": [statement.to_dict() for statement in self.statements],
            "variables": [variable.to_dict() for variable in self.variables]
        }


class CDeclarator:
    def __init__(self, identifier: CIdentifier | NoneNode, type: CType, initializer: Node | list[Node] = NoneNode()):
        self.identifier: CIdentifier | NoneNode = identifier
        self.type: CType = type

    @property
    def child(self) -> CType:
        return self.type

    @child.setter
    def child(self, value: CType):
        self.type = value

    def to_dict(self):
        return {
            "node": "CDeclarator",
            "name": str(self.identifier) if not isinstance(self.identifier, NoneNode) else self.identifier.to_dict(),
            "type": self.type.to_dict()
        }

    def get_child_bottom(self) -> Node:
        return self.type.get_child_bottom() if not isinstance(self.type, NoneNode) else self


class CArray:
    def __init__(self, size: Node, array_of: CType):
        self.size: Node = size
        self.__array_of: CType = array_of

    def to_dict(self):
        return {
            "node": "CArray",
            "size": self.size.to_dict(),
            "array_of": self.__array_of.to_dict()
        }

    def get_child_bottom(self) -> CType:
        try:
            return self.child.get_child_bottom()
        except AttributeError:
            return self.child if not isinstance(self.child, NoneNode) else self

    @property
    def child(self) -> CType:
        return self.__array_of

    @child.setter
    def child(self, value: CType):
        self.__array_of = value

    def copy(self):
        return CArray(self.size, self.__array_of)

    def get_bottom_not_array(self):
        if isinstance(self.child, CArray):
            return self.child.get_bottom_not_array()
        else:
            return self.child


class CPointer:
    def __init__(self, pointer_level: int, qualifiers: CQualifierKind, pointer_of: CType):
        self.pointer_level: int = pointer_level
        self.qualifiers: CQualifierKind = qualifiers
        self.__pointer_of: CType = pointer_of

    @property
    def child(self) -> CType:
        return self.__pointer_of

    @child.setter
    def child(self, value: CType):
        self.__pointer_of = value

    def to_dict(self):
        return {
            "node": "CPointer",
            "pointer_level": self.pointer_level,
            "qualifiers": self.qualifiers.to_dict(),
            "pointer_of": self.child.to_dict()
        }

    def get_child_bottom(self) -> CType:
        try:
            return self.child.get_child_bottom()
        except AttributeError:
            return self.child if not isinstance(self.child, NoneNode) else self


class CFunction:
    def __init__(self, identifier: CIdentifier | NoneNode, parameters: list[CParameter], return_type: CType):
        self.identifier: CIdentifier | NoneNode = identifier
        self.parameters: list[CParameter] = parameters
        self.return_type: CType = return_type

    def to_dict(self):
        return {
            "node": "CFunction",
            "name": str(self.identifier) if not isinstance(self.identifier, NoneNode) else self.identifier.to_dict(),
            "parameters": [parameter.to_dict() for parameter in self.parameters],
            "return_type": self.return_type.to_dict()
        }

    @property
    def child(self) -> CType:
        return self.return_type

    @child.setter
    def child(self, value: CType):
        self.return_type = value

    def get_child_bottom(self) -> CType:
        try:
            return self.child.get_child_bottom()
        except AttributeError:
            return self.child if not isinstance(self.child, NoneNode) else self


class FunctionCall:
    def __init__(self, function: CFunction, parameters_type: list):
        self.function: CFunction = function
        self.parameters_type: list = parameters_type


CSpecifierType = Union[CPrimitiveDataTypes, CStruct, CUnion, CEnum, CTypedef, NoneNode]
CType = Union[CFunction, CPointer, CArray, CPrimitiveDataTypes, CStruct, CUnion, CEnum, CTypedef, NoneNode]
CParameter = CDeclarator

Node = Union[
    NoneNode,
    Block,
    CEnum,
    CEnumMember,
    Variable,
    Number,
    CString,
    CIdentifier,
    CTernaryOp,
    CBinaryOp,
    CUnaryOp,
    CCast,
    FunctionCall,
    CPointer,
    CArray,
    CFunction,
    CParameter
]

specifier_cases: dict[CSpecifierKind.Void, CPrimitiveDataTypes] = {
    CSpecifierKind.Void: CPrimitiveDataTypes.Void,

    # char kinds
    CSpecifierKind.Char: CPrimitiveDataTypes.Char,
    CSpecifierKind.Signed + CSpecifierKind.Char: CPrimitiveDataTypes.Char,
    CSpecifierKind.Unsigned + CSpecifierKind.Char: CPrimitiveDataTypes.UChar,
    CSpecifierKind.Unsigned + CSpecifierKind.Char: CPrimitiveDataTypes.UChar,

    # short kinds
    CPrimitiveDataTypes.Short: CPrimitiveDataTypes.Short,
    CSpecifierKind.Short + CSpecifierKind.Int: CPrimitiveDataTypes.Short,
    CSpecifierKind.Signed + CSpecifierKind.Short: CPrimitiveDataTypes.Short,
    CSpecifierKind.Signed + CSpecifierKind.Short + CSpecifierKind.Int: CPrimitiveDataTypes.Short,
    CSpecifierKind.Unsigned + CSpecifierKind.Short: CPrimitiveDataTypes.UShort,
    CSpecifierKind.Unsigned + CSpecifierKind.Short + CSpecifierKind.Int: CPrimitiveDataTypes.UShort,

    # int X64WIN kinds
    CSpecifierKind.Int: CPrimitiveDataTypes.Int,
    CSpecifierKind.Signed: CPrimitiveDataTypes.Int,
    CSpecifierKind.Signed + CSpecifierKind.Int: CPrimitiveDataTypes.Int,
    CSpecifierKind.Long: CPrimitiveDataTypes.Int,
    CSpecifierKind.Long + CSpecifierKind.Int: CPrimitiveDataTypes.Int,
    CSpecifierKind.Signed + CSpecifierKind.Long: CPrimitiveDataTypes.Int,
    CSpecifierKind.Signed + CSpecifierKind.Long + CSpecifierKind.Int: CPrimitiveDataTypes.Int,
    CSpecifierKind.Unsigned: CPrimitiveDataTypes.UInt,
    CSpecifierKind.Unsigned + CSpecifierKind.Int: CPrimitiveDataTypes.UInt,
    CSpecifierKind.Unsigned + CSpecifierKind.Long: CPrimitiveDataTypes.Int,
    CSpecifierKind.Unsigned + CSpecifierKind.Long + CSpecifierKind.Int: CPrimitiveDataTypes.Int,

    # long kinds
    CSpecifierKind.Long + CSpecifierKind.Long: CPrimitiveDataTypes.Long,
    CSpecifierKind.Long + CSpecifierKind.Long + CSpecifierKind.Int: CPrimitiveDataTypes.Long,
    CSpecifierKind.Signed + CSpecifierKind.Long + CSpecifierKind.Long: CPrimitiveDataTypes.Long,
    CSpecifierKind.Signed + CSpecifierKind.Long + CSpecifierKind.Long + CSpecifierKind.Int: CPrimitiveDataTypes.Long,
    CSpecifierKind.Unsigned + CSpecifierKind.Long + CSpecifierKind.Long: CPrimitiveDataTypes.ULong,
    CSpecifierKind.Unsigned + CSpecifierKind.Long + CSpecifierKind.Long + CSpecifierKind.Int: CPrimitiveDataTypes.ULong,

    # float and double
    CSpecifierKind.Float: CPrimitiveDataTypes.Float,
    CSpecifierKind.Double: CPrimitiveDataTypes.Double,
    CSpecifierKind.Long + CSpecifierKind.Double: CPrimitiveDataTypes.LongDouble,
}
