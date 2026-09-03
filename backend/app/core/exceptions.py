class PulseCryptError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthError(PulseCryptError):
    def __init__(self, message: str = "authentication failed", status_code: int = 401):
        super().__init__(message, status_code)


class IntegrityError(PulseCryptError):
    def __init__(self, message: str = "integrity check failed", status_code: int = 409):
        super().__init__(message, status_code)


class ForbiddenError(PulseCryptError):
    def __init__(self, message: str = "insufficient privileges", status_code: int = 403):
        super().__init__(message, status_code)


class NotFoundError(PulseCryptError):
    def __init__(self, message: str = "not found", status_code: int = 404):
        super().__init__(message, status_code)
