import shutil
from pathlib import Path
from unittest import TestCase

from baca2PackageManager.zipper import Zip


class UnzipTest(TestCase):
    def setUp(self) -> None:
        self.path = Path('./test_packages')
        if not self.path.is_dir():
            self.path = Path('./tests/test_packages')
        self.src = self.path / 'zip_src'
        self.dist = self.path / 'zip_dst'
        shutil.rmtree(self.dist, ignore_errors=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.dist, ignore_errors=True)

    def test_01_simple_unzip(self):
        with Zip(self.src / 'zok.zip') as zip_f:
            zip_f.extractall(self.dist)
        dir_path = Path(self.dist / 'zok')
        self.assertTrue(dir_path.is_dir())
        arr = [f for f in dir_path.iterdir()]
        self.assertEqual(len(arr), 3)
        with open(dir_path / '1.txt', 'r') as f:
            self.assertEqual(f.read(), 'zok/1.txt ok')
        with open(dir_path / '2.txt', 'r') as f:
            self.assertEqual(f.read(), 'zok/2.txt ok')
        with open(dir_path / '3.txt', 'r') as f:
            self.assertEqual(f.read(), 'zok/3.txt ok')

    def test_02_zipbomb_detection(self):
        with Zip(self.src / 'zbsm.zip') as zip_f:
            with self.assertRaises(Zip.UnsafeZipFile):
                zip_f.extractall(self.dist)

    def test_03_nested_zipfile_extraction(self):
        with Zip(self.src / 'znest.zip') as zip_f:
            zip_f.extractall(self.dist)
        dir_path = Path(self.dist / 'znest')
        self.assertTrue(dir_path.is_dir())
        arr = [f for f in dir_path.iterdir()]
        self.assertEqual(len(arr), 3)
        with open(dir_path / '1.txt', 'r') as f:
            self.assertEqual(f.read(), 'zok/1.txt ok')
        with open(dir_path / '2.txt', 'r') as f:
            self.assertEqual(f.read(), 'zok/2.txt ok')
        with open(dir_path / '3.txt', 'r') as f:
            self.assertEqual(f.read(), 'zok/3.txt ok')

    def test_04_nested_zipfile_without_leave_top(self):
        with Zip(self.src / 'znest.zip') as zip_f:
            zip_f.extractall(self.dist, leave_top=False)
        dir_path = Path(self.dist)
        self.assertTrue(dir_path.is_dir())
        arr = [f for f in dir_path.iterdir()]
        self.assertEqual(len(arr), 3)
        with open(dir_path / '1.txt', 'r') as f:
            self.assertEqual(f.read(), 'zok/1.txt ok')
        with open(dir_path / '2.txt', 'r') as f:
            self.assertEqual(f.read(), 'zok/2.txt ok')
        with open(dir_path / '3.txt', 'r') as f:
            self.assertEqual(f.read(), 'zok/3.txt ok')