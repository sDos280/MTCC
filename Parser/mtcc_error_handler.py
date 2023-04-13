import Parser.mtcc_token as tk
import Parser.mtcc_lexer as lx


class ErrorHandler:
    def __init__(self, lexer: lx.Lexer):
        self.lexer: lx.Lexer = lexer

    def syntax_error(self, before_token: tk.Token, expected_token_string: str, string: str) -> None:
        line_string = self.lexer.get_line_string(self.lexer.get_token_line(before_token))
        print(string)
        print(len(line_string) * " " + "^")
        print(len(line_string) * " " + expected_token_string)
