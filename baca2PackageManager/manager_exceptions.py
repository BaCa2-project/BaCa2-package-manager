class FileAlreadyExist(Exception):
    pass


class NoTestFound(Exception):
    pass


class NoSetFound(Exception):
    pass


class TestExistError(FileAlreadyExist):
    pass


class InvalidFileExtension(Exception):
    pass
