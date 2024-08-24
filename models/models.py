class CodeElement:
    def __init__(self, element_type: str, name: str, code: str, lineno: int):
        self.type = element_type
        self.name = name
        self.code = code
        self.lineno = int