class BaseAppError(Exception):
    status_code = 500
    error_type = "server_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AlreadyExistsError(BaseAppError):
    status_code = 409
    error_type = "already_exists"
