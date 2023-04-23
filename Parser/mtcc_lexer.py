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

                    if self.is_char('/'):
                        str_ += self.current_char
                        self.peek_char()  # peek / char

                        break

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

    def peek_operator_or_separator(self) -> tk.Token:
        index_: int = self.index
        str_: str = self.current_char

        self.peek_char()  # peek first char

        while not self.is_char(END_OF_FILE) and str_ in tk.string_to_separator_or_operator.keys():
            str_ += self.current_char
            self.peek_char()

        # we peek one too much char
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
            elif self.is_char_operator_or_separator():
                token: tk.Token = self.peek_operator_or_separator()
                self.tokens.append(token)
            else:
                self.peek_char()

        self.tokens.append(tk.Token(tk.TokenKind.END, len(self.file_string) - 1, '\0'))
