class PersonException(Exception):
    def __init__(self, message: str):
        self.message = message


class PersonNotFound(PersonException):
    ...
