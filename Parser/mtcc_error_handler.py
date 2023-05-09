class PrimaryExpressionNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SpecifierQualifierListNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class TypeQualifierNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SpecifierQualifierListInvalid(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SpecifierQualifierListEmpty(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class TokenExpected(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
