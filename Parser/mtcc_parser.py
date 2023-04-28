from __future__ import annotations

from typing import Union
import enum

import Parser.mtcc_token as tk


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


class CEnumMember:
    def __init__(self, name: str, value: int):
        self.name: str = name
        self.value: int = value

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


class Function:
    def __init__(self, name: str, parameters_type: list):
        self.name: str = name
        self.parameters_type: list = parameters_type

    def __str__(self):
        str_ = f"{self.name}("
        for parameter in self.parameters_type:
            str_ += f"{parameter}, "

        str_ = str_[0:-2]
        str_ += ")"

        return str_


class FunctionCall:
    def __init__(self, function: Function, parameters_type: list):
        self.function: Function = function
        self.parameters_type: list = parameters_type

    def __str__(self):
        str_ = f"{self.function.name}("
        for parameter in self.parameters_type:
            str_ += f"{parameter}, "

        str_ = str_[0:-2]
        str_ += ")"

        return str_


Node = Union[Block, CEnum, CEnumMember, Variable, Number, String, Identifier, CTernaryOp, CBinaryOp, CUnaryOp, FunctionCall, Function]


class Parser:
    def __init__(self, tokens: list[tk.Token]):
        self.tokens: list[tk.Token] = tokens
        self.current_token: tk.Token | None = None
        self.index: int = -1

        self.current_block: Block | None = None

        self.enums: list[CEnum] = []
        self.variables: list[Variable] = []  # variables declension list
        self.function_declension: list[Function] = []
        self.function: list[Function]  # functions ast code

    def peek_token(self) -> None:  # increase the index and update the current token
        self.index += 1
        self.current_token = self.tokens[self.index]

    def drop_token(self) -> None:  # decrease the index and update the current token
        self.index -= 1
        self.current_token = self.tokens[self.index]

    def is_token_kind(self, kind: tk.TokenKind) -> bool:
        return self.current_token.kind == kind

    def expect_token_kind(self, kind: tk.TokenKind, error_string) -> None:
        assert False, "Not implemented"

    def is_variable_in_block(self, variable: Variable) -> bool:
        if self.current_block is None:  # we are on the top level block
            for var in self.variables:
                if variable.name == var.name:
                    return True
        else:
            for var in self.current_block.variables:
                if variable.name == var.name:
                    return True

        return False

    def peek_primary_expression(self) -> Node:
        if self.is_token_kind(tk.TokenKind.INTEGER_LITERAL):
            number: Number = Number(int(self.current_token.string))
            self.peek_token()  # peek integer literal number
            return number
        elif self.is_token_kind(tk.TokenKind.FLOAT_LITERAL):
            number: Number = Number(int(self.current_token.string))
            self.peek_token()  # peek float literal number
            return number
        elif self.is_token_kind(tk.TokenKind.STRING_LITERAL):
            string_: String = String(self.current_token.string)
            self.peek_token()  # peek string literal number
            return string_
        elif self.is_token_kind(tk.TokenKind.Identifier):
            assert False, "Not implemented, need to add variable exist check"
            identifier: Identifier = Identifier(self.current_token.string)
            self.peek_token()  # peek identifier literal number
            return identifier
        elif self.is_token_kind(tk.TokenKind.OPENING_CURLY_BRACE):
            self.peek_token()  # peek opening curly brace token

            expression: Node = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.CLOSING_CURLY_BRACE, "Expecting a closing curly brace")

            self.peek_token()  # peek closing curly brace token

            return expression
        else:
            raise SyntaxError("Expected a primary expression token")

    def peek_postfix_expression(self) -> Node:
        primary_expression: Node = self.peek_primary_expression()

        if not isinstance(primary_expression, Identifier):
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

    def peek_cast_expression(self):
        if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            assert False, "Not implemented"

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

                multiplicative_expression = CBinaryOp(CBinaryOpKind.Addition, multiplicative_expression, sub_multiplicative_expression)

            elif self.is_token_kind(tk.TokenKind.HYPHEN):
                self.peek_token()  # peek the - token

                sub_multiplicative_expression: Node = self.peek_multiplicative_expression()

                multiplicative_expression = CBinaryOp(CBinaryOpKind.Subtraction, multiplicative_expression, sub_multiplicative_expression)
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

                relational_expression = CBinaryOp(CBinaryOpKind.EqualTo, relational_expression, sub_relational_expression)

            elif self.is_token_kind(tk.TokenKind.NE_OP):
                self.peek_token()  # peek the != token

                sub_relational_expression: Node = self.peek_relational_expression()

                relational_expression = CBinaryOp(CBinaryOpKind.NotEqualTo, relational_expression, sub_relational_expression)

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

            exclusive_or_expression = CBinaryOp(CBinaryOpKind.BitwiseOR, exclusive_or_expression, sub_exclusive_or_expression)

        return exclusive_or_expression

    def peek_logical_and_expression(self) -> Node:
        inclusive_or_expression: Node = self.peek_inclusive_or_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.AND_OP):
                self.peek_token()  # peek the && token

                sub_inclusive_or_expression: Node = self.peek_inclusive_or_expression()

                inclusive_or_expression = CBinaryOp(CBinaryOpKind.LogicalAND, inclusive_or_expression, sub_inclusive_or_expression)
            else:
                return inclusive_or_expression

    def peek_logical_or_expression(self) -> Node:
        logical_and_expression: Node = self.peek_logical_and_expression()

        while self.is_token_kind(tk.TokenKind.OR_OP):
            self.peek_token()  # peek the || token

            sub_logical_and_expression: Node = self.peek_logical_and_expression()

            logical_and_expression = CBinaryOp(CBinaryOpKind.LogicalOR, logical_and_expression, sub_logical_and_expression)

        return logical_and_expression

    def peek_conditional_expression(self) -> Node:
        logical_or_expression: Node = self.peek_logical_or_expression()

        if self.is_token_kind(tk.TokenKind.QUESTION_MARK):
            self.peek_token()  # peek the ? token

            expression: Node = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.COLON, "Expected ':' in conditional expression")

            conditional_expression: Node = self.peek_conditional_expression()

            return CTernaryOp(logical_or_expression, expression, conditional_expression)

        return logical_or_expression

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
            self.peek_token()  # peek the opening curly brace token

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
                enum: CEnum = self.peek_enum_specifier()
                self.enums.append(enum)
                self.expect_token_kind(tk.TokenKind.SEMICOLON, "A semicolon is needed")
            else:
                self.peek_token()

            if statement is not None:
                self.AST.append(statement)
