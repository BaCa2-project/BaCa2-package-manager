from unittest import TestCase

from baca2PackageManager.tools import bytes_to_str


class ToolsTest(TestCase):
    def test_bytes_to_str(self):
        self.assertEqual(bytes_to_str(1), '1B')
        self.assertEqual(bytes_to_str(512), '512B')
        self.assertEqual(bytes_to_str(1024), '1.00K')
        self.assertEqual(bytes_to_str(1536), '1.50K')
        self.assertEqual(bytes_to_str(1024 ** 2), '1.00M')
        self.assertEqual(bytes_to_str(1024 ** 3), '1.00G')

    def test_bytes_to_str_zero(self):
        self.assertEqual(bytes_to_str(0), '0B')