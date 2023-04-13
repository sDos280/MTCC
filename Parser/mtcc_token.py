import enum


# note: TK => Token Type

class TokenKind(enum.Enum):
    # Comments(syntax)
    SingleLineComment = enum.auto()  # // ... \n
    BlockComment = enum.auto()  # /* ... */

    # Keywords
    Typedef = enum.auto()
    Enum = enum.auto()  # enum
    For = enum.auto()  # for
    While = enum.auto()  # while
    If = enum.auto()  # if
    # Keywords for types
    Const = enum.auto()
    Int = enum.auto()  # int
    Float = enum.auto()  # float

    # Separators
    OpenParenthesis = enum.auto()  # (
    CloseParenthesis = enum.auto()  # )
    OpenBrace = enum.auto()  # {
    CloseBrace = enum.auto()  # }
    Comma = enum.auto()  # ,
    Dot = enum.auto()  # .
    Semicolon = enum.auto()  # ;

    # Operators
    Equal = enum.auto()  # =
    PlusSign = enum.auto()  # +
    MinusSign = enum.auto()  # -
    Asterisk = enum.auto()  # *
    ForwardSlash = enum.auto()  # /

    # Literals
    IntegerLiteral = enum.auto()
    FloatLiteral = enum.auto()

    # Identifier
    Identifier = enum.auto()

    EndOfTokens = enum.auto()  # End Of Tokens stream token


# string to keyword dictionary
string_to_keyword: dict[str, TokenKind] = {
    # the token hierarchy is by string len
    "typedef": TokenKind.Typedef,
    "const": TokenKind.Const,
    "while": TokenKind.While,
    "float": TokenKind.Float,
    "enum": TokenKind.Enum,
    "int": TokenKind.Int,
    "for": TokenKind.For,
    "if": TokenKind.If,
}

# string to separator dictionary
string_to_separator: dict[str, TokenKind] = {
    # the token hierarchy is by string length
    "(": TokenKind.OpenParenthesis,
    ")": TokenKind.CloseParenthesis,
    "{": TokenKind.OpenBrace,
    "}": TokenKind.CloseBrace,
    ",": TokenKind.Comma,
    ".": TokenKind.Dot,
    ";": TokenKind.Semicolon
}

# string to operator dictionary
string_to_operator: dict[str, TokenKind] = {
    # the token hierarchy is by string length
    "=": TokenKind.Equal,
    "+": TokenKind.PlusSign,
    "-": TokenKind.MinusSign,
    "*": TokenKind.Asterisk,
    "/": TokenKind.ForwardSlash,
}


class Token:
    def __init__(self, kind: TokenKind, start: int, length: int, string: str):
        self.kind: TokenKind = kind
        self.start: int = start  # the start char index
        self.length: int = length  # the length of chars of the token in the file
        self.string: str = string  # the string of the token in the file (for debugging)
