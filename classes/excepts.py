class ProviderHttpError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"ProviderHttpError [{self.status_code}]: {self.message}"


class ProviderTypeError(Exception):
    def __init__(self, message, expected_type):
        self.message = message
        self.expected_type = expected_type

    def __str__(self):
        return f"ProviderTypeError: {self.message} (expected {self.expected_type})"


class SimklTypeError(Exception):
    def __init__(self, message, expected_type):
        self.message = message
        self.expected_type = expected_type

    def __str__(self):
        return f"SimklTypeError: {self.message} (expected {self.expected_type})"


__all__ = ["ProviderHttpError", "ProviderTypeError", "SimklTypeError"]
