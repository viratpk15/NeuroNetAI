"""Domain-level exceptions. Kept independent of any web framework so the
domain and application layers never import FastAPI."""


class NeuroNetError(Exception):
    """Base class for all application-raised errors."""


class NotFoundError(NeuroNetError):
    def __init__(self, entity: str, identifier: str):
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} with id '{identifier}' was not found")


class ValidationError(NeuroNetError):
    def __init__(self, message: str):
        super().__init__(message)


class ConflictError(NeuroNetError):
    def __init__(self, message: str):
        super().__init__(message)
