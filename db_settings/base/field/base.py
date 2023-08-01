from typing import Any


class Field:
    def __init__(self, default: Any, description: str = None):
        self.default = default
        self.description = description
