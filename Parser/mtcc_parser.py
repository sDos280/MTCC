from __future__ import annotations

import Parser.mtcc_error_handler as eh
import Parser.mtcc_token as tk
from Parser.mtcc_c_ast import *


class Parser:
    def __init__(self, tokens: list[tk.Token], source_string: str):
        self.tokens: list[tk.Token] = tokens
        for token_index in range(len(self.tokens)):
            self.tokens[token_index].index = token_index
        self.current_token: tk.Token | None = None
        self.index: int = -1

        self.source_string: str = source_string

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

    def is_token_kind(self, kind: list[tk.TokenKind] | tk.TokenKind) -> bool:
        if isinstance(kind, tk.TokenKind):
            return self.current_token.kind == kind
        else:
            return self.current_token.kind in kind

    def is_token_type_specifier(self) -> bool:
        return self.is_token_kind(
            [tk.TokenKind.VOID,
             tk.TokenKind.CHAR,
             tk.TokenKind.SHORT,
             tk.TokenKind.INT,
             tk.TokenKind.LONG,
             tk.TokenKind.FLOAT,
             tk.TokenKind.DOUBLE,
             tk.TokenKind.SIGNED,
             tk.TokenKind.UNSIGNED,
             tk.TokenKind.STRUCT,
             tk.TokenKind.UNION,
             tk.TokenKind.ENUM,
             tk.TokenKind.Identifier])

    def is_token_type_qualifier(self) -> bool:
        return self.is_token_kind(
            [tk.TokenKind.CONST,
             tk.TokenKind.VOLATILE])

    def is_specifier_qualifier_list(self) -> bool:
        return self.is_token_type_specifier() or self.is_token_type_qualifier()

    def get_line_string(self, line: int) -> str:
        lines: list[str] = self.source_string.split('\n')
        if line <= len(lines):
            return lines[line]
        else:
            return ""

    def get_line_substring_at_index(self, index: int) -> str:
        # find the beginning of the line containing the index
        start_of_line = self.source_string.rfind('\n', 0, index) + 1 if '\n' in self.source_string[:index] else 0
        return self.source_string[start_of_line:index]

    def fatal_token(self, token_location: int, error_string: str, raise_exception) -> None:
        line_string: str = self.get_line_string(self.tokens[token_location].line)
        sub_line_string: str = self.get_line_substring_at_index(self.tokens[token_location].start)  # the sub line right up to the token start
        full_error_string: str = f"\nMTCC:{self.tokens[token_location].line + 1}:{len(sub_line_string) + 1}: "
        full_error_string += error_string + '\n'
        full_error_string += f"    | {line_string}\n"
        full_error_string += f"    | {len(sub_line_string) * ' '}^{(len(self.tokens[token_location].string) - 1) * '~'}"
        raise raise_exception(full_error_string)

    def expect_token_kind(self, kind: list[tk.TokenKind] | tk.TokenKind, error_string: str, raise_exception) -> None:
        if not self.is_token_kind(kind):
            self.fatal_token(self.index, error_string, raise_exception)

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

    def specifier_list_to_ctype_specifier(self, token_specifiers_list: list[tk.Token]) -> CSpecifierType:
        """convert a valid specifier list to a ctype specifier, make sure that you remove all the Signed specifier before calling this function"""
        match len(token_specifiers_list):
            case 1:
                match token_specifiers_list[0].kind:
                    case tk.TokenKind.VOID:
                        return CPrimitiveDataTypes.Void
                    case tk.TokenKind.CHAR:
                        return CPrimitiveDataTypes.Short
                    case tk.TokenKind.SHORT:
                        return CPrimitiveDataTypes.Char
                    case tk.TokenKind.INT:
                        return CPrimitiveDataTypes.Int
                    case tk.TokenKind.LONG:
                        return CPrimitiveDataTypes.Long
                    case tk.TokenKind.FLOAT:
                        return CPrimitiveDataTypes.Float
                    case tk.TokenKind.DOUBLE:
                        return CPrimitiveDataTypes.Double
                    case tk.TokenKind.STRUCT:
                        assert False, "Not implemented"
                    case tk.TokenKind.UNION:
                        assert False, "Not implemented"
                    case tk.TokenKind.ENUM:
                        assert False, "Not implemented"
                    case tk.TokenKind.Identifier:
                        assert False, "there is a need to check if the identifier is a typedef"
                        assert False, "Not implemented"
                    case _:
                        self.fatal_token(self.current_token.index, "Invalid token type specifier", SyntaxError)
            case 2:
                match token_specifiers_list[0].kind:
                    case tk.TokenKind.UNSIGNED:
                        match token_specifiers_list[1].kind:
                            case tk.TokenKind.SHORT:
                                return CPrimitiveDataTypes.UShort
                            case tk.TokenKind.CHAR:
                                return CPrimitiveDataTypes.UChar
                            case tk.TokenKind.INT:
                                return CPrimitiveDataTypes.UInt
                            case tk.TokenKind.LONG:
                                return CPrimitiveDataTypes.ULong
                            case _:
                                self.fatal_token(token_specifiers_list[1].index, "Invalid token type specifier", SyntaxError)
                    case tk.TokenKind.LONG:
                        match token_specifiers_list[1].kind:
                            case tk.TokenKind.LONG:
                                return CPrimitiveDataTypes.LongLong
                            case tk.TokenKind.INT:
                                return CPrimitiveDataTypes.Int
                            case tk.TokenKind.DOUBLE:
                                return CPrimitiveDataTypes.LongDouble
                            case _:
                                self.fatal_token(token_specifiers_list[1].index, "Invalid token type specifier", SyntaxError)
                    case _:
                        self.fatal_token(token_specifiers_list[0].index, "Invalid token type specifier", SyntaxError)
            case 3:
                match token_specifiers_list[0].kind:
                    case tk.TokenKind.UNSIGNED:
                        match token_specifiers_list[1].kind:
                            case tk.TokenKind.LONG:
                                match token_specifiers_list[2].kind:
                                    case tk.TokenKind.LONG:
                                        return CPrimitiveDataTypes.ULongLong
                                    case _:
                                        self.fatal_token(token_specifiers_list[2].index, "Invalid token type specifier", SyntaxError)
                            case _:
                                self.fatal_token(token_specifiers_list[1].index, "Invalid token type specifier", SyntaxError)
                    case tk.TokenKind.LONG:
                        match token_specifiers_list[1].kind:
                            case tk.TokenKind.LONG:
                                match token_specifiers_list[2].kind:
                                    case tk.TokenKind.INT:
                                        return CPrimitiveDataTypes.LongLong
                                    case _:
                                        self.fatal_token(token_specifiers_list[2].index, "Invalid token type specifier", SyntaxError)
                            case _:
                                self.fatal_token(token_specifiers_list[1].index, "Invalid token type specifier", SyntaxError)
                    case _:
                        self.fatal_token(token_specifiers_list[0].index, "Invalid token type specifier", SyntaxError)

    @staticmethod
    def is_specifier_list_valid(specifier_list: list[tk.Token]) -> bool:
        """check if a specifier list is valid"""
        long_count: int = 0
        signed_count: int = 0
        unsigned_count: int = 0

        for specifier in specifier_list:

            match specifier.kind:
                case tk.TokenKind.VOID:
                    return long_count == 0 and signed_count == 0 and unsigned_count == 0
                case tk.TokenKind.UNSIGNED:
                    unsigned_count += 1
                    if signed_count != 0:
                        return False
                case tk.TokenKind.SIGNED:
                    signed_count += 1
                    if unsigned_count != 0:
                        return False
                case tk.TokenKind.SHORT:
                    return long_count == 0
                case tk.TokenKind.CHAR:
                    return long_count == 0
                case tk.TokenKind.INT:
                    return long_count <= 2
                case tk.TokenKind.LONG:
                    long_count += 1
                    if long_count > 2:
                        return False
                case tk.TokenKind.FLOAT:
                    return long_count == 0 and signed_count == 0 and unsigned_count == 0
                case tk.TokenKind.DOUBLE:
                    return long_count <= 1 and signed_count == 0 and unsigned_count == 0
                case tk.TokenKind.STRUCT:
                    return long_count == 0 and signed_count == 0 and unsigned_count == 0
                case tk.TokenKind.UNION:
                    return long_count == 0 and signed_count == 0 and unsigned_count == 0
                case tk.TokenKind.ENUM:
                    return long_count == 0 and signed_count == 0 and unsigned_count == 0
                case tk.TokenKind.Identifier:
                    return long_count == 0 and signed_count == 0 and unsigned_count == 0

        return False

    def peek_token_type_qualifier(self) -> tk.Token:
        self.expect_token_kind([tk.TokenKind.CONST, tk.TokenKind.VOLATILE], "Expected a type qualifier token", eh.TypeQualifierNotFound)
        token: tk.Token = self.current_token
        self.peek_token()  # peek the token
        return token

    def peek_token_type_specifier(self) -> tk.Token:
        self.expect_token_kind(
            [
                tk.TokenKind.VOID,
                tk.TokenKind.CHAR,
                tk.TokenKind.SHORT,
                tk.TokenKind.INT,
                tk.TokenKind.LONG,
                tk.TokenKind.FLOAT,
                tk.TokenKind.DOUBLE,
                tk.TokenKind.SIGNED,
                tk.TokenKind.UNSIGNED,
                tk.TokenKind.STRUCT,
                tk.TokenKind.UNION,
                tk.TokenKind.ENUM,
                tk.TokenKind.Identifier
            ],
            "Expected a type specifier token",
            eh.TypeSpecifierNotFound
        )
        token: tk.Token = self.current_token
        self.peek_token()  # peek the token
        return token

    def peek_specifier_qualifier_list(self) -> list[tk.Token]:
        specifier_qualifier_list: list[tk.Token] = []
        while True:
            if self.is_token_type_qualifier():
                type_qualifier: tk.Token = self.peek_token_type_qualifier()
                specifier_qualifier_list.append(type_qualifier)
            elif self.is_token_type_specifier():
                type_specifier: tk.Token = self.peek_token_type_specifier()
                specifier_qualifier_list.append(type_specifier)
            else:
                if len(specifier_qualifier_list) == 0:
                    self.fatal_token(self.current_token.start, "Expected a type qualifier or a type specifier", eh.SpecifierQualifierListEmpty)
                return specifier_qualifier_list

    def peek_type_name(self) -> CTypeName:
        specifier_qualifier_list: list[tk.Token] = self.peek_specifier_qualifier_list()

        specifier_list: list[tk.Token] = list(
            filter(
                lambda s: s.kind != tk.TokenKind.SIGNED and s.kind != tk.TokenKind.CONST and s.kind != tk.TokenKind.VOLATILE,
                specifier_qualifier_list
            )
        )

        if len(specifier_list) == 0:
            self.fatal_token(self.current_token.index, "Expected a type specifier", eh.TypeSpecifierNotFound)

        specifier: CSpecifierType = self.specifier_list_to_ctype_specifier(specifier_list)

        qualifiers_list: list[tk.Token] = list(
            filter(
                lambda q: q.kind == tk.TokenKind.CONST or q == tk.TokenKind.VOLATILE,
                specifier_qualifier_list
            )
        )

        is_const: bool = False
        is_volatile: bool = False
        for qualifier in qualifiers_list:
            if qualifier.kind == tk.TokenKind.CONST:
                is_const = True
            elif qualifier.kind == tk.TokenKind.VOLATILE:
                is_volatile = True

        return CTypeName(is_const, is_volatile, specifier, None)

    def peek_primary_expression(self) -> Node:
        if self.is_token_kind(tk.TokenKind.INTEGER_LITERAL):
            number: Number = Number(int(self.current_token.string))
            self.peek_token()  # peek integer literal number
            return number
        elif self.is_token_kind(tk.TokenKind.FLOAT_LITERAL):
            number: Number = Number(float(self.current_token.string))
            self.peek_token()  # peek float literal number
            return number
        elif self.is_token_kind(tk.TokenKind.STRING_LITERAL):
            string_: String = String(self.current_token.string)
            self.peek_token()  # peek string literal number
            return string_
        elif self.is_token_kind(tk.TokenKind.Identifier):
            identifier: Identifier = Identifier(self.current_token.string)
            self.peek_token()  # peek identifier literal number
            return identifier
        elif self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek opening parenthesis token

            expression: Node = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expecting a closing curly brace", eh.TokenExpected)

            self.peek_token()  # peek closing parenthesis token

            return expression
        else:
            raise eh.PrimaryExpressionNotFound("Expected a primary expression token")

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

    def peek_cast_expression(self) -> Node:

        if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek ( token

            if self.is_token_type_qualifier() or self.is_token_type_specifier():
                type_name: CTypeName = self.peek_type_name()
            else:  # not a cast but a "(" expression ")"
                # we need to drop a token
                self.drop_token()  # drop to the ( token
                unary_expression: Node = self.peek_unary_expression()
                return unary_expression

            self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expecting a closing parenthesis", eh.TokenExpected)

            self.peek_token()  # peek ) token

            cast_expression: Node = self.peek_cast_expression()

            return CCast(type_name, cast_expression)

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

            self.expect_token_kind(tk.TokenKind.COLON, "Expected ':' in conditional expression", eh.TokenExpected)

            self.peek_token()  # peek the : token 

            conditional_expression: Node = self.peek_conditional_expression()

            return CTernaryOp(logical_or_expression, expression, conditional_expression)

        return logical_or_expression

    def peek_assignment_expression(self) -> Node:
        conditional_expression: Node = self.peek_conditional_expression()

        if self.is_assignment_operator():
            self.peek_token()  # peek assignment operator token

            sub_assignment_expression: Node = self.peek_assignment_expression()

            return CBinaryOp(self.get_binary_assignment_op_kind_(), conditional_expression, sub_assignment_expression)
        else:
            return conditional_expression

    def is_assignment_operator(self) -> bool:
        return self.is_token_kind(tk.TokenKind.EQUALS) or \
               self.is_token_kind(tk.TokenKind.MUL_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.DIV_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.MOD_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.ADD_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.SUB_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.LEFT_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.RIGHT_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.AND_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.XOR_ASSIGN) or \
               self.is_token_kind(tk.TokenKind.OR_ASSIGN)

    def get_binary_assignment_op_kind_(self) -> CBinaryOpKind:
        if self.is_token_kind(tk.TokenKind.EQUALS):
            return CBinaryOpKind.Assignment
        elif self.is_token_kind(tk.TokenKind.MUL_ASSIGN):
            return CBinaryOpKind.MultiplicationAssignment
        elif self.is_token_kind(tk.TokenKind.DIV_ASSIGN):
            return CBinaryOpKind.DivisionAssignment
        elif self.is_token_kind(tk.TokenKind.MOD_ASSIGN):
            return CBinaryOpKind.ModulusAssignment
        elif self.is_token_kind(tk.TokenKind.ADD_ASSIGN):
            return CBinaryOpKind.AdditionAssignment
        elif self.is_token_kind(tk.TokenKind.SUB_ASSIGN):
            return CBinaryOpKind.SubtractionAssignment
        elif self.is_token_kind(tk.TokenKind.LEFT_ASSIGN):
            return CBinaryOpKind.LeftShiftAssignment
        elif self.is_token_kind(tk.TokenKind.RIGHT_ASSIGN):
            return CBinaryOpKind.RightShiftAssignment
        elif self.is_token_kind(tk.TokenKind.AND_ASSIGN):
            return CBinaryOpKind.BitwiseAndAssignment
        elif self.is_token_kind(tk.TokenKind.XOR_ASSIGN):
            return CBinaryOpKind.BitwiseXorAssignment
        elif self.is_token_kind(tk.TokenKind.OR_ASSIGN):
            return CBinaryOpKind.BitwiseOrAssignment
        else:
            raise Exception("Invalid assignment operator token")

    def peek_expression(self) -> Node | list[Node]:
        assignment_expressions: list[Node] = []
        assignment_expression: Node = self.peek_assignment_expression()

        if self.is_token_kind(tk.TokenKind.COMMA):
            assignment_expressions.append(assignment_expression)

        while self.is_token_kind(tk.TokenKind.COMMA):
            self.peek_token()  # peek the , token

            sub_assignment_expression: Node = self.peek_assignment_expression()

            assignment_expressions.append(sub_assignment_expression)

        if len(assignment_expressions) != 0:
            return assignment_expressions
        else:
            return assignment_expression

    def peek_constant_expression(self) -> Node:
        conditional_expression: Node = self.peek_conditional_expression()
        return conditional_expression

    def peek_enumerator(self, enum: CEnum) -> CEnumMember:
        self.expect_token_kind(tk.TokenKind.Identifier, "Expecting an identifier")

        enum.current_member_value += 1
        name: str = self.current_token.string

        self.peek_token()  # peek identifier token

        member: CEnumMember = CEnumMember(name, enum.current_member_value)

        if self.is_token_kind(tk.TokenKind.EQUALS):
            self.peek_token()  # peek the equal token

            member_assigned_value: Node = self.peek_constant_expression()

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

        expression = self.peek_expression()

        print(expression)
        """while not (self.current_token is None or self.is_token_kind(tk.TokenKind.END)):
            statement = None

            if self.is_token_kind(tk.TokenKind.ENUM):
                enum: CEnum = self.peek_enum_specifier()
                self.enums.append(enum)
                self.expect_token_kind(tk.TokenKind.SEMICOLON, "A semicolon is needed")
            else:
                self.peek_token()"""
