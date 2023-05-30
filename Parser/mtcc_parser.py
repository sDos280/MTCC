from __future__ import annotations

import Parser.mtcc_error_handler as eh
import Parser.mtcc_token as tk
from Parser.mtcc_c_ast import *
import json


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
        self.function_declension: list[CFunction] = []
        self.function: list[CFunction]  # functions ast code

    def peek_token(self) -> None:  # increase the index and update the current token
        self.index += 1
        self.current_token = self.tokens[self.index]

    def drop_token(self) -> None:  # decrease the index and update the current token
        self.index -= 1
        self.current_token = self.tokens[self.index]

    def set_index_token(self, index: int) -> None:
        self.index = index
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
             tk.TokenKind.IDENTIFIER])

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
        sub_line_string: str = self.get_line_substring_at_index(
            self.tokens[token_location].start)  # the sub line right up to the token start
        full_error_string: str = f"\nMTCC:{self.tokens[token_location].line + 1}:{len(sub_line_string) + 1}: "
        full_error_string += error_string + '\n'
        full_error_string += f"    | {line_string}\n"
        full_error_string += f"    | {len(sub_line_string) * ' '}^{(len(self.tokens[token_location].string) - 1) * '~'}"
        raise raise_exception(full_error_string)

    def expect_token_kind(self, kind: list[tk.TokenKind] | tk.TokenKind, error_string: str, raise_exception) -> None:
        if not self.is_token_kind(kind):
            self.fatal_token(self.index, error_string, raise_exception)

    def token_to_seperator_kind(self) -> CSpecifierKind:
        if self.is_token_kind(tk.TokenKind.VOID):
            return CSpecifierKind.Void
        elif self.is_token_kind(tk.TokenKind.SHORT):
            return CSpecifierKind.Short
        elif self.is_token_kind(tk.TokenKind.CHAR):
            return CSpecifierKind.Char
        elif self.is_token_kind(tk.TokenKind.INT):
            return CSpecifierKind.Int
        elif self.is_token_kind(tk.TokenKind.LONG):
            return CSpecifierKind.Long
        elif self.is_token_kind(tk.TokenKind.FLOAT):
            return CSpecifierKind.Float
        elif self.is_token_kind(tk.TokenKind.DOUBLE):
            return CSpecifierKind.Double
        elif self.is_token_kind(tk.TokenKind.SIGNED):
            return CSpecifierKind.Signed
        elif self.is_token_kind(tk.TokenKind.UNSIGNED):
            return CSpecifierKind.Unsigned
        else:
            return CSpecifierKind(0)

    def is_abstract_declarator(self) -> bool:
        """check if the current token is an abstract declarator starter"""
        return self.is_token_kind(
            [tk.TokenKind.ASTERISK, tk.TokenKind.OPENING_PARENTHESIS, tk.TokenKind.OPENING_BRACKET])

    def is_direct_abstract_declarator(self) -> bool:
        """check if the current token is a direct abstract declarator starter"""
        return self.is_token_kind([tk.TokenKind.OPENING_PARENTHESIS, tk.TokenKind.OPENING_BRACKET])

    def peek_token_type_qualifier(self) -> tk.Token:
        self.expect_token_kind([tk.TokenKind.CONST, tk.TokenKind.VOLATILE], "Expected a type qualifier token",
                               eh.TypeQualifierNotFound)
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
                tk.TokenKind.IDENTIFIER
            ],
            "Expected a type specifier token",
            eh.TypeSpecifierNotFound
        )
        token: tk.Token = self.current_token
        self.peek_token()  # peek the token
        return token

    def peek_specifier_qualifier_list(self) -> CSpecifierType:
        # the idea is form https://github.com/sgraham/dyibicc/blob/main/src/parse.c#L359
        specifier_counter: CSpecifierKind = 0
        qualifier_counter: CQualifierKind = 0
        type: CSpecifierType = 0

        while self.is_token_type_specifier() or self.is_token_type_qualifier():
            # handel qualifiers
            # TODO: make a way that those qualifiers will be really used
            if self.is_token_type_qualifier():
                if self.is_token_kind(tk.TokenKind.CONST):
                    qualifier_counter |= CQualifierKind.Const
                elif self.is_token_kind(tk.TokenKind.VOLATILE):
                    qualifier_counter |= CQualifierKind.Volatile
                self.peek_token()  # peek the qualifier token

            # handle struct, union, enum and typename identifier
            # when parsing those specifiers the specifier count should be 0
            if self.is_token_kind(tk.TokenKind.STRUCT) or \
                    self.is_token_kind(tk.TokenKind.UNION) or \
                    self.is_token_kind(tk.TokenKind.ENUM) or \
                    self.is_token_kind(tk.TokenKind.IDENTIFIER):
                if specifier_counter != 0:
                    self.fatal_token(self.current_token.index, "Invalid specifier in that current contex",
                                     eh.SpecifierQualifierListInvalid)

                # TODO: implement and return the CSpecifierType
                if self.is_token_kind(tk.TokenKind.STRUCT):
                    assert False, "Not implemented"
                elif self.is_token_kind(tk.TokenKind.UNION):
                    assert False, "Not implemented"
                elif self.is_token_kind(tk.TokenKind.ENUM):
                    assert False, "Not implemented"
                elif self.is_token_kind(tk.TokenKind.IDENTIFIER):
                    assert False, "Not implemented"

            current_specifier_kind: CSpecifierKind = self.token_to_seperator_kind()
            if current_specifier_kind == CSpecifierKind.Signed or current_specifier_kind == current_specifier_kind.Unsigned:
                specifier_counter |= current_specifier_kind
            else:
                specifier_counter += current_specifier_kind

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

            specifier_type: CPrimitiveDataTypes = specifier_cases.get(specifier_counter)

            if specifier_type is None:
                self.fatal_token(self.current_token.index,
                                 "Invalid specifier in that current contex",
                                 eh.SpecifierQualifierListInvalid
                                 )
            else:
                type = specifier_type

            self.peek_token()  # peek the specifier token

        if type == 0:
            self.fatal_token(self.current_token.index,
                             "Invalid specifier in that current contex",
                             eh.SpecifierQualifierListInvalid
                             )
        else:
            return type

    def peek_type_name(self) -> CTypeName:
        specified_qualifier: CSpecifierType = self.peek_specifier_qualifier_list()

        abstract_declarator: AbstractType = None
        if self.is_abstract_declarator():
            abstract_declarator: AbstractType = self.peek_abstract_declarator()
            abstract_declarator.get_child_bottom().child = specified_qualifier

        return CTypeName(False, False, abstract_declarator if abstract_declarator is not None else specified_qualifier)

    def peek_parameter_type_list(self) -> list[CParameter]:
        if self.is_abstract_declarator():
            raise SyntaxError("Expected a parameter type list")
        else:
            return list[CParameter]()

    def peek_abstract_declarator(self) -> AbstractType:
        if self.is_direct_abstract_declarator():
            return self.peek_direct_abstract_declarator()
        elif self.is_token_kind(tk.TokenKind.ASTERISK):
            pointer_level: int = 0
            while self.is_token_kind(tk.TokenKind.ASTERISK):
                self.peek_token()  # peek * token
                pointer_level += 1

            if self.is_direct_abstract_declarator():
                direct_abstract_declarator: AbstractType = self.peek_direct_abstract_declarator()
                direct_abstract_declarator.get_child_bottom().child = CAbstractPointer(pointer_level, None)
                return direct_abstract_declarator
            else:
                return CAbstractPointer(pointer_level, None)

    def peek_direct_abstract_declarator(self) -> AbstractType:
        # return the top and bottom of the direct abstract declarator
        direct_abstract_declarator_module: AbstractType = self.peek_direct_abstract_declarator_module()
        direct_abstract_declarator: AbstractType = direct_abstract_declarator_module
        while True:
            if self.is_direct_abstract_declarator():
                direct_abstract_declarator_module: AbstractType = self.peek_direct_abstract_declarator_module()
                if isinstance(direct_abstract_declarator_module, list):  # need to convert direct_abstract_declarator_module to CFuncion
                    direct_abstract_declarator.get_child_bottom().child = CFunction(None, direct_abstract_declarator_module, None)
                else:
                    direct_abstract_declarator.get_child_bottom().child = direct_abstract_declarator_module
            else:
                return direct_abstract_declarator

    def peek_direct_abstract_declarator_module(self) -> AbstractType | list[CParameter]:
        """
        direct_abstract_declarator_module
            : '(' abstract_declarator ')'
            | '[' ']'
            | '[' constant_expression ']'
            | '(' ')'
            | '(' parameter_type_list ')'
            ;
        """
        if self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek ( token
            if self.is_token_kind(tk.TokenKind.CLOSING_PARENTHESIS):
                self.peek_token()  # peek ) token

                return list[CParameter]()
            else:
                index_before_peek: int = self.current_token.index
                try:
                    parameter_type_list: list[CParameter] = self.peek_parameter_type_list()
                    self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected a ) token", eh.TokenExpected)
                    self.peek_token()  # peek ) token

                    return parameter_type_list
                except:
                    self.set_index_token(index_before_peek)
                    abstract_declarator: AbstractType = self.peek_abstract_declarator()
                    self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expected a ) token", eh.TokenExpected)
                    self.peek_token()  # peek ) token

                    return abstract_declarator
        elif self.is_token_kind(tk.TokenKind.OPENING_BRACKET):
            self.peek_token()  # peek [ token
            if self.is_token_kind(tk.TokenKind.CLOSING_BRACKET):
                self.peek_token()  # peek ] token

                return CAbstractArray(None, None)
            else:
                constant_expression: Node = self.peek_constant_expression()
                self.expect_token_kind(tk.TokenKind.CLOSING_BRACKET, "Expected a ] token", eh.TokenExpected)
                self.peek_token()  # peek ] token
                return CAbstractArray(constant_expression, None)
        else:
            self.fatal_token(self.current_token.index, "Expected a ( or [ token", eh.TokenExpected)

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
            string_: CString = CString(self.current_token.string)
            self.peek_token()  # peek string literal number
            return string_
        elif self.is_token_kind(tk.TokenKind.IDENTIFIER):
            identifier: CIdentifier = CIdentifier(self.current_token)
            self.peek_token()  # peek identifier literal number
            return identifier
        elif self.is_token_kind(tk.TokenKind.OPENING_PARENTHESIS):
            self.peek_token()  # peek opening parenthesis token

            expression: Node = self.peek_expression()

            self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expecting a closing curly brace",
                                   eh.TokenExpected)

            self.peek_token()  # peek closing parenthesis token

            return expression
        else:
            raise eh.PrimaryExpressionNotFound("Expected a primary expression token")

    def peek_postfix_expression(self) -> Node:
        primary_expression: Node = self.peek_primary_expression()

        if not isinstance(primary_expression, CIdentifier):
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
                # TODO: need to check if the specifier (of token identifiers) is a typedef in not that should be an unary expression
                type_name: CTypeName = self.peek_type_name()
            else:  # not a cast but a "(" expression ")"
                # we need to drop a token
                self.drop_token()  # drop to the ( token
                unary_expression: Node = self.peek_unary_expression()
                return unary_expression

            self.expect_token_kind(tk.TokenKind.CLOSING_PARENTHESIS, "Expecting a closing parenthesis",
                                   eh.TokenExpected)

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

                multiplicative_expression = CBinaryOp(CBinaryOpKind.Addition, multiplicative_expression,
                                                      sub_multiplicative_expression)

            elif self.is_token_kind(tk.TokenKind.HYPHEN):
                self.peek_token()  # peek the - token

                sub_multiplicative_expression: Node = self.peek_multiplicative_expression()

                multiplicative_expression = CBinaryOp(CBinaryOpKind.Subtraction, multiplicative_expression,
                                                      sub_multiplicative_expression)
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

                relational_expression = CBinaryOp(CBinaryOpKind.EqualTo, relational_expression,
                                                  sub_relational_expression)

            elif self.is_token_kind(tk.TokenKind.NE_OP):
                self.peek_token()  # peek the != token

                sub_relational_expression: Node = self.peek_relational_expression()

                relational_expression = CBinaryOp(CBinaryOpKind.NotEqualTo, relational_expression,
                                                  sub_relational_expression)

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

            exclusive_or_expression = CBinaryOp(CBinaryOpKind.BitwiseOR, exclusive_or_expression,
                                                sub_exclusive_or_expression)

        return exclusive_or_expression

    def peek_logical_and_expression(self) -> Node:
        inclusive_or_expression: Node = self.peek_inclusive_or_expression()

        while True:
            if self.is_token_kind(tk.TokenKind.AND_OP):
                self.peek_token()  # peek the && token

                sub_inclusive_or_expression: Node = self.peek_inclusive_or_expression()

                inclusive_or_expression = CBinaryOp(CBinaryOpKind.LogicalAND, inclusive_or_expression,
                                                    sub_inclusive_or_expression)
            else:
                return inclusive_or_expression

    def peek_logical_or_expression(self) -> Node:
        logical_and_expression: Node = self.peek_logical_and_expression()

        while self.is_token_kind(tk.TokenKind.OR_OP):
            self.peek_token()  # peek the || token

            sub_logical_and_expression: Node = self.peek_logical_and_expression()

            logical_and_expression = CBinaryOp(CBinaryOpKind.LogicalOR, logical_and_expression,
                                               sub_logical_and_expression)

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
        self.expect_token_kind(tk.TokenKind.IDENTIFIER, "Expecting an identifier")

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

        if self.is_token_kind(tk.TokenKind.IDENTIFIER):
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

        print(json.dumps(expression.to_dict(), indent=2))
        """while not (self.current_token is None or self.is_token_kind(tk.TokenKind.END)):
            statement = None

            if self.is_token_kind(tk.TokenKind.ENUM):
                enum: CEnum = self.peek_enum_specifier()
                self.enums.append(enum)
                self.expect_token_kind(tk.TokenKind.SEMICOLON, "A semicolon is needed")
            else:
                self.peek_token()"""
