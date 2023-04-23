import Parser.mtcc_token as tk

END_OF_FILE = '\0'


class Lexer:
    def __init__(self, main_file_path: str) -> None:
        main_file = open(main_file_path)
        self.file_string: str = main_file.read()
        self.file_string += END_OF_FILE
        main_file.close()

        self.index: int = 0
        self.current_char: str = None
        self.tokens: list[tk.Token] = []

    def is_char(self, string: str) -> bool:
        return self.current_char in string

    def lex(self):
        while self.index < self.file_string_length:
            self.peek_token()

        self.tokens.append(tk.Token(tk.TokenKind.END, len(self.file_string) - 1, '\0'))
