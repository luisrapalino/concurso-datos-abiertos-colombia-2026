class DomainError(Exception):
    """Base class for domain-level failures."""


class EntityNotFoundError(DomainError):
    """Raised when a requested domain entity does not exist."""

    def __init__(self, entity: str, identifier: str) -> None:
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} not found: {identifier}")


class ServiceUnavailableError(DomainError):
    """Raised when an upstream dependency is unavailable."""

    def __init__(self, service: str, reason: str | None = None) -> None:
        self.service = service
        self.reason = reason
        message = f"{service} is unavailable"
        if reason:
            message = f"{message}: {reason}"
        super().__init__(message)
