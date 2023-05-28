class ProviderHttpError(Exception):
    """Exception for HTTP errors from providers"""

    def __init__(self, message, status_code):
        """Params"""
        self.message = message
        self.status_code = status_code

    def __str__(self):
        """String representation"""
        return f"ProviderHttpError [{self.status_code}]: {self.message}"


class ProviderTypeError(Exception):
    """Exception for type errors from providers"""

    def __init__(self, message, expected_type):
        """Params"""
        self.message = message
        self.expected_type = expected_type

    def __str__(self):
        """String representation"""
        return f"ProviderTypeError: {self.message} (expected {self.expected_type})"


class SimklTypeError(Exception):
    """Exception for type errors from providers"""

    def __init__(self, message, expected_type):
        """Params"""
        self.message = message
        self.expected_type = expected_type

    def __str__(self):
        """String representation"""
        return f"SimklTypeError: {self.message} (expected {self.expected_type})"


class MediaIsNsfw(Exception):
    """Media is NSFW exception"""


__all__ = ["ProviderHttpError", "ProviderTypeError", "SimklTypeError"]
