import Parser.mtcc_token as tk


class lexer:
    def __init__(self, main_file_path: str) -> None:
        main_file = open(main_file_path)
        self.file_string: str = main_file.read()
        self.file_string_length = len(self.file_string) + 1
        self.file_string += '\0'
        main_file.close()

        self.index: int = 0
        self.tokens: list[tk.Token] = []

    @property
    def char(self):  # for debugging
        return self.file_string[self.index]

    def get_string_from_source(self, start: int, length: int):
        return self.file_string[start: start + length]

    def get_token_string_with_kind(self, token: tk.Token):
        return self.file_string[token.start: token.start + token.length] + " " + str(token.kind)

    def peek_char(self, offset: int) -> str:
        return self.file_string[self.index + offset]

    def peek_oneline_comment(self) -> tk.Token:
        token = tk.Token(tk.TokenKind.SingleLineComment, self.index, 2, "")

        while self.index < self.file_string_length and self.peek_char(0) not in ['\r',
                                                                                 '\n']:  # will not keep the '\r' | '\n' char
            self.index += 1
            token.length += 1

        token.string = self.get_string_from_source(token.start, token.length)

        return token

    def peek_block_comment(self) -> tk.Token:
        token = tk.Token(tk.TokenKind.BlockComment, self.index, 2, "")

        while self.index < self.file_string_length and not (
                self.peek_char(-2) == '*' and self.peek_char(-1) == '/'):  # will keep the "*/"
            self.index += 1
            token.length += 1

        token.string = self.get_string_from_source(token.start, token.length)

        return token

    def peek_number(self) -> tk.Token:
        length_: int = 0
        dot_count: int = 0
        self_index_copy: int = self.index

        while self.index < self.file_string_length and (self.peek_char(0) == '.' or self.peek_char(0) in "0123456789"):
            if self.peek_char(-1) == '.':
                dot_count += 1
            if dot_count == 2:
                break

            self.index += 1
            length_ += 1

        if dot_count == 1:
            token = tk.Token(tk.TokenKind.FloatLiteral, self_index_copy, length_,
                             self.get_string_from_source(self_index_copy, length_))
        else:
            token = tk.Token(tk.TokenKind.IntegerLiteral, self_index_copy, length_,
                             self.get_string_from_source(self_index_copy, length_))

        return token

    def peek_identifier_or_keyword(self) -> tk.Token:
        length_: int = 0
        self_index_copy: int = self.index

        while self.index < self.file_string_length and (self.peek_char(0).isalnum() or self.peek_char(0) == "_"):
            self.index += 1
            length_ += 1

        token_string = self.file_string[self_index_copy: self_index_copy + length_]

        if token_string in tk.string_to_keyword.keys():
            token = tk.Token(tk.string_to_keyword[token_string], self_index_copy, length_,
                             self.get_string_from_source(self_index_copy, length_))
        else:  # identifier
            token = tk.Token(tk.TokenKind.Identifier, self_index_copy, length_,
                             self.get_string_from_source(self_index_copy, length_))

        return token

    def peek_separator_or_operator(self) -> tk.Token:
        length_: int = 0
        self_index_copy: int = self.index

        while self.index < self.file_string_length and self.peek_char(0) in "=+-*/(){},.;":
            self.index += 1
            length_ += 1

            token_string = self.file_string[self_index_copy: self_index_copy + length_]
            if token_string in tk.string_to_separator.keys() or token_string in tk.string_to_operator.keys():
                break

        token_string = self.file_string[self_index_copy: self_index_copy + length_]

        if token_string in tk.string_to_separator.keys():
            token = tk.Token(tk.string_to_separator[token_string], self_index_copy, length_,
                             self.get_string_from_source(self_index_copy, length_))
        elif token_string in tk.string_to_operator.keys():  # operator
            token = tk.Token(tk.string_to_operator[token_string], self_index_copy, length_,
                             self.get_string_from_source(self_index_copy, length_))
        else:
            raise SyntaxError("Invalid operator / seperator")

        return token

    def peek_token(self):

        if self.peek_char(0) in [' ', '\r', '\n', '\0']:
            self.index += 1

        elif self.peek_char(0) == '/' and self.peek_char(1) == '/':
            self.tokens.append(self.peek_oneline_comment())
        elif self.peek_char(0) == '/' and self.peek_char(1) == '*':
            self.tokens.append(self.peek_block_comment())

        elif self.peek_char(0).isnumeric():
            self.tokens.append(self.peek_number())

        elif self.peek_char(0).isalpha() or self.peek_char(0) == "_":
            self.tokens.append(self.peek_identifier_or_keyword())

        elif self.peek_char(0) in "=+-*/(){},.;":
            self.tokens.append(self.peek_separator_or_operator())

        else:
            self.index += 1

    def lex(self):
        while self.index < self.file_string_length:
            self.peek_token()

        self.tokens.append(tk.Token(tk.TokenKind.EndOfTokens, self.file_string_length - 1, 1, '\0'))
