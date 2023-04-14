import Parser.mtcc_token as tk
import Parser.mtcc_lexer as lx


class ErrorHandler:
    def __init__(self, lexer: lx.Lexer):
        self.lexer: lx.Lexer = lexer

    def expect_token_syntax_error(self, before_token: tk.Token, expected_token_string: str, error_string: str) -> None:
        token_line: int = self.lexer.get_token_line(before_token)
        token_position_in_line: int = self.lexer.get_token_position_in_line(before_token)
        line_string: str = self.lexer.get_line_string(token_line)
        offset = token_position_in_line + before_token.length
        if before_token.length == 1:
            offset -= 1
        print(f"Syntax Error:{token_line}:{token_position_in_line + before_token.length + 1}: ", error_string)
        print(line_string)
        print(offset * " " + "^")
        print(offset * " " + expected_token_string)
        exit(1)
