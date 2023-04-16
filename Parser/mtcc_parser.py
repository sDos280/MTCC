from __future__ import annotations

import enum

import Parser.mtcc_token as tk
import Parser.mtcc_error_handler as eh
from typing import Union


class Parser:
    def __init__(self, tokens: list[tk.Token], error_handler: eh.ErrorHandler):
        self.tokens: list[tk.Token] = tokens
        self.current_token: tk.Token = None
        self.error_handler: eh.ErrorHandler = error_handler
        self.index: int = -1
        self.AST: list[Statement] = []

    def peek_token(self) -> None:  # increase the index and update the current token
        self.index += 1
        self.current_token = self.tokens[self.index]

    def drop_token(self) -> None:  # decrease the index and update the current token
        self.index -= 1
        self.current_token = self.tokens[self.index]
