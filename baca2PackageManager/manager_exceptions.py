from pathlib import Path


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


class PackageCreationFailed(Exception):
    def __init__(self, e, **kwargs):
        super().__init__(self.message(e, **kwargs))

    @staticmethod
    def message(e: Exception, **kwargs) -> str:
        msg = 'Package creation failed: '
        if isinstance(e, FileNotFoundError):
            filename = str(e).split()[-1].replace('\'', '')
            path = Path(filename)
            msg += f'File \'{path.relative_to(kwargs.get("root_path"))}\' not found'
        else:
            msg += str(e)
        return msg
