import Parser.mtcc_token as tk

END_OF_FILE = '\0'


class Lexer:
    def __init__(self, main_file_path: str) -> None:
        main_file = open(main_file_path)
        self.file_string: str = main_file.read()
        self.file_string += END_OF_FILE
        main_file.close()

        self.index: int = 0
        self.current_char: str = self.file_string[self.index]
        self.current_line: int = 0  # the first line is 0
        self.tokens: list[tk.Token] = []
        self.comments: list[tk.Token] = []

    def peek_char(self):
        if self.is_char('\n'):
            self.current_line += 1

        self.index += 1
        self.current_char = self.file_string[self.index]

    def drop_char(self):
        self.index -= 1
        self.current_char = self.file_string[self.index]

        if self.is_char('\n'):
            self.current_line -= 1

    def is_char(self, string: str) -> bool:
        return self.current_char in string

    def is_char_whitespace(self) -> bool:
        return self.current_char in "\n\t\r "

    def is_char_numeric(self) -> bool:
        return self.current_char.isnumeric()

    def is_char_identifier_starter(self) -> bool:
        return self.current_char.isalpha() or self.is_char('_')

    def is_char_identifier(self) -> bool:
        return self.current_char.isalnum() or self.is_char('_')

    def is_char_operator_or_separator(self) -> bool:
        return self.is_char("+-*/%&|^~<>!=?:,.;{}[]()")

    def peek_comment(self):

        index_: int = self.index
        str_: str = ""

        if self.is_char('/'):  # a one line comment
            str_ += self.current_char
            self.peek_char()  # peek / char

            if self.is_char('/'):  # a one line comment
                while not self.is_char(END_OF_FILE):
                    if self.is_char('\n'):  # check for comment end
                        str_ += self.current_char
                        self.peek_char()  # peek \n char

                        break

                    str_ += self.current_char
                    self.peek_char()  # peek comment char

            elif self.is_char('*'):  # a block comment
                str_ += self.current_char
                self.peek_char()  # peek * char

                while not self.is_char(END_OF_FILE):
                    if self.is_char('*'):  # check for block comment end
                        str_ += self.current_char
                        self.peek_char()  # peek * char

                        if not self.is_char(END_OF_FILE):
                            if self.is_char('/'):
                                str_ += self.current_char
                                self.peek_char()  # peek / char

                                break
                        else:
                            raise SyntaxError(f"An block comment ender in needed, file index: {self.index}")

                    str_ += self.current_char
                    self.peek_char()  # peek comment's char
            else:
                raise SyntaxError(f"An comment starter in needed, file index: {self.index}")

        return tk.Token(tk.TokenKind.COMMENT, index_, self.current_line - 1, str_)

    def peek_number(self):
        index_: int = self.index
        dot_count: int = 0
        str_: str = self.current_char

        self.peek_char()  # peek first char

        while not self.is_char(END_OF_FILE) and (self.is_char_numeric() or self.is_char('.')):
            if self.is_char('.'):
                dot_count += 1

            if dot_count == 2:
                break

            str_ += self.current_char
            self.peek_char()  # peek numeric/dot char

        if dot_count == 0:  # An integer
            return tk.Token(tk.TokenKind.INTEGER_LITERAL, index_, self.current_line, str_)
        else:
            return tk.Token(tk.TokenKind.FLOAT_LITERAL, index_, self.current_line, str_)

    def peek_identifier(self):
        index_: int = self.index
        str_: str = self.current_char

        self.peek_char()  # peek first char

        while not self.is_char(END_OF_FILE):
            if not self.is_char_identifier():
                break

            str_ += self.current_char
            self.peek_char()  # peek identifier char

        return tk.Token(tk.TokenKind.IDENTIFIER, index_, self.current_line, str_)

    def peek_string_literal(self):
        index_: int = self.index
        str_: str = self.current_char
        opener: str = self.current_char
        start_line: int = self.current_line

        self.peek_char()  # peek first char

        while True:
            if self.is_char(opener):
                str_ += self.current_char
                self.peek_char()  # peek "opener" char
                break

            if self.is_char(END_OF_FILE):
                raise SyntaxError(f"An string/char literal ender in needed, file index: {self.index}")

            if self.is_char('\\'):  # escape sequences
                str_ += self.current_char
                self.peek_char()  # peek / char

                if self.is_char(END_OF_FILE):
                    raise SyntaxError(f"An string/char literal ender in needed, file index: {self.index}")

                if self.is_char('\''):  # single quote
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += self.current_char
                    self.peek_char()  # peek ' char

                elif self.is_char('\"'):  # double  quote
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += self.current_char
                    self.peek_char()  # peek " char

                elif self.is_char('?'):  # question mark
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += self.current_char
                    self.peek_char()  # peek ? char

                elif self.is_char('\\'):  # backslash
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += self.current_char
                    self.peek_char()  # peek \ char

                elif self.is_char('a'):  # alert (bell) character
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += '\a'
                    self.peek_char()  # peek a char

                elif self.is_char('b'):  # backspace
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += '\b'
                    self.peek_char()  # peek b char

                elif self.is_char('f'):  # form feed
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += '\f'
                    self.peek_char()  # peek f char

                elif self.is_char('n'):  # newline (line feed)
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += '\n'
                    self.peek_char()  # peek n char

                elif self.is_char('r'):  # carriage return
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += '\r'
                    self.peek_char()  # peek r char

                elif self.is_char('t'):  # horizontal tab
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += '\t'
                    self.peek_char()  # peek t char

                elif self.is_char('v'):  # vertical tab
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += '\v'
                    self.peek_char()  # peek v char

                elif self.is_char('0'):  # null character
                    str_ = str_[0:-1]  # remove the \ char
                    str_ += '\0'
                    self.peek_char()  # peek 0 char

                elif self.is_char('x'):  # hexadecimal representation of a character
                    # TODO: Implement escape sequences of hexadecimal representation of a character
                    assert False, "Not implemented"
                continue

            str_ += self.current_char
            self.peek_char()  # peek char

        return tk.Token(tk.TokenKind.STRING_LITERAL, index_, self.current_line if start_line == self.current_line else self.current_line - 1, str_)

    def peek_operator_or_separator(self) -> tk.Token:
        index_: int = self.index
        str_: str = self.current_char

        self.peek_char()  # peek first char

        while not self.is_char(END_OF_FILE) and self.is_char_operator_or_separator():
            str_ += self.current_char
            self.peek_char()

            if str_ not in tk.string_to_separator_or_operator.keys():
                str_ = str_[0:-1]
                self.drop_char()  # drop the last char
                break

        return tk.Token(tk.string_to_separator_or_operator[str_], index_, self.current_line, str_)

    def lex(self):
        while not self.is_char(END_OF_FILE):
            if self.is_char_whitespace():
                self.peek_char()
            elif self.is_char_numeric():
                token: tk.Token = self.peek_number()
                self.tokens.append(token)
            elif self.is_char_identifier_starter():
                token: tk.Token = self.peek_identifier()
                if token.string in tk.string_to_keyword.keys():
                    keyword_kind: tk.TokenKind = tk.string_to_keyword[token.string]
                    token.kind = keyword_kind
                self.tokens.append(token)
            elif self.is_char('\'\"'):
                token: tk.Token = self.peek_string_literal()
                self.tokens.append(token)
            elif self.is_char('/'):  # comment
                index: int = self.index
                line: int = self.current_line
                try:
                    token: tk.Token = self.peek_comment()
                    self.comments.append(token)
                except SyntaxError:  # operator
                    self.index = index
                    self.current_line = line
                    self.current_char = self.file_string[self.index]
                    token: tk.Token = self.peek_operator_or_separator()
                    self.tokens.append(token)
            elif self.is_char_operator_or_separator():
                token: tk.Token = self.peek_operator_or_separator()
                self.tokens.append(token)
            else:
                if self.is_char(END_OF_FILE):
                    break
                raise SyntaxError(f"Unexpected character: {self.current_char}, file index: {self.index}")

        self.tokens.append(tk.Token(tk.TokenKind.END, len(self.file_string) - 1, self.current_line, '\0'))
