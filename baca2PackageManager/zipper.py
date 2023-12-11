import shutil
from pathlib import Path
from typing import Iterable

from importlib.resources.abc import StrPath
from zipfile import ZipFile, ZipInfo


class Zip(ZipFile):
    class UnsafeZipFile(Exception):
        """
        Exception raised when the zip file is unsafe.
        """
        pass

    ZIPBOMB_RATIO = 20

    @property
    def uncompressed_size(self) -> int:
        """
        Returns the size of the compressed data.

        :return: Size of the compressed data in bytes [B].
        :rtype: int
        """
        return sum([data.file_size for data in self.filelist])

    @property
    def compressed_size(self) -> int:
        """
        Returns the size of the uncompressed data.

        :return: Size of the uncompressed data in bytes [B].
        :rtype: int
        """
        return sum([data.compress_size for data in self.filelist])

    def check_zip_bomb(self) -> None:
        """
        Checks if the zip bomb is present in the zip file.

        :param max_size: Maximum size of the compressed data in bytes [B].
        :type max_size: int
        :return: True if the zip bomb is present, False otherwise.
        :rtype: bool
        """
        if self.uncompressed_size / self.compressed_size > self.ZIPBOMB_RATIO:
            raise self.UnsafeZipFile('Zip bomb detected.')

    def move_to_top(self, path: StrPath | Path, leave_top: bool = True) -> None:
        """
        Shreds the 1 directory chain from zip file. To be called after zip extraction.

        :return: None
        """
        path = Path(path) if isinstance(path, str) else path

        path_glob = list(path.glob('*'))
        if len(path_glob) == 1:
            sub_path = path_glob[0]
            if leave_top:
                self.move_to_top(sub_path, False)
                return
            mv_path = path.parent / f'{path.name}_bak'
            shutil.rmtree(mv_path, ignore_errors=True)
            shutil.move(sub_path, mv_path)
            shutil.rmtree(path, ignore_errors=True)
            mv_path.rename(path)

            # org_name = path.name
            # path.rename(path.parent / f'{org_name}_bak')
            # sub_path = list(path.glob('*'))[0]
            # sub_path.rename(path.parent / org_name)
            # path.rmdir()
            self.move_to_top(path, False)

    def extractall(
            self,
            path: StrPath | None = ...,
            members: Iterable[str | ZipInfo] | None = None,
            pwd: bytes | None = ...,
            leave_top: bool = True
    ):
        """
        Extract all members from the archive to the current working
        directory. `path' specifies a different directory to extract to.
        `members' is optional and must be a subset of the list returned
        by namelist().
        """
        self.check_zip_bomb()
        super().extractall(path, members, pwd)
        self.move_to_top(path, leave_top)

