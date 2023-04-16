class MyAnimeListHttpError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"MyAnimeListHttpError [{self.status_code}]: {self.message}"


class MyAnimeListTypeError(Exception):
    def __init__(self, message, expected_type):
        self.message = message
        self.expected_type = expected_type

    def __str__(self):
        return f"MyAnimeListTypeError: {self.message} (expected {self.expected_type})"


