import Parser.mtcc_token as tk

END_OF_FILE = '\0'


class Lexer:
    def __init__(self, main_file_path: str) -> None:
        main_file = open(main_file_path)
        self.file_string: str = main_file.read()
        self.file_string += END_OF_FILE
        main_file.close()

        self.index: int = -1
        self.current_char: str = None
        self.tokens: list[tk.Token] = []

    def peek_char(self):
        self.index += 1
        self.current_char = self.file_string[self.index]

    def drop_char(self):
        self.index -= 1
        self.current_char = self.file_string[self.index]

    def is_char(self, string: str) -> bool:
        return self.current_char in string

    def is_char_whitespace(self) -> bool:
        return self.current_char in "\n\t\r\0 "

    def is_char_numeric(self) -> bool:
        return self.current_char.isnumeric()

    def is_char_operator_or_separator(self) -> bool:
        return self.is_char("+-*/%&|^~<>!=?:,.;{}[]()")

    def peek_comment(self):
        index_: int = self.index
        str_: str = self.current_char

        self.peek_char()  # peek first char

        if self.is_char('*'):  # a block comment
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
                self.peek_char()  # peek comment char

        else:  # a one line comment
            while not self.is_char(END_OF_FILE):
                if self.is_char('\n'):  # check for comment end
                    str_ += self.current_char
                    self.peek_char()  # peek \n char

                    break

                str_ += self.current_char
                self.peek_char()  # peek comment char

        return tk.Token(tk.TokenKind.COMMENT, index_, str_)

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
            return tk.Token(tk.TokenKind.INTEGER_LITERAL, index_, str_)
        else:
            return tk.Token(tk.TokenKind.FLOAT_LITERAL, index_, str_)

    def peek_string_literal(self):
        index_: int = self.index
        str_: str = self.current_char
        opener: str = self.current_char

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

        return tk.Token(tk.TokenKind.STRING_LITERAL, index_, str_)

    def peek_operator_or_separator(self) -> tk.Token:
        index_: int = self.index
        str_: str = self.current_char

        self.peek_char()  # peek first char

        while not self.is_char(END_OF_FILE) and str_ in tk.string_to_separator_or_operator.keys() and self.is_char_operator_or_separator():
            str_ += self.current_char
            self.peek_char()

        # we peek one too much char
        if self.index != len(self.file_string) - 1 and len(str_) > 1:  # we need to drop only if we aren't on the last char (not including \0)
            self.drop_char()
            str_ = str_[0:-1]

        return tk.Token(tk.string_to_separator_or_operator[str_], index_, str_)

    def lex(self):
        self.peek_char()  # initiate the current char

        while not self.is_char(END_OF_FILE):
            if self.is_char_whitespace():
                self.peek_char()
            elif self.is_char('/'):
                token: tk.Token = self.peek_comment()
                self.tokens.append(token)
            elif self.is_char_numeric():
                token: tk.Token = self.peek_number()
                self.tokens.append(token)
            elif self.is_char('\'\"'):
                token: tk.Token = self.peek_string_literal()
                self.tokens.append(token)
            elif self.is_char_operator_or_separator():
                token: tk.Token = self.peek_operator_or_separator()
                self.tokens.append(token)
            else:
                self.peek_char()

        self.tokens.append(tk.Token(tk.TokenKind.END, len(self.file_string) - 1, '\0'))
